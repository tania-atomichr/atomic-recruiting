#!/usr/bin/env python3
"""Teamtailor candidate-summary helper.

Subcommands:
  extract <share_url_or_candidate_id> [--out FILE]
      Fetch the interview transcript (from the public share page), the CV text
      (from the resume PDF via API), and the trusted recruiter-filled fields
      (english-level CEFR, years-of-experience, salary-expectations). Prints a
      JSON bundle for the model to write the summary from.

  write <candidate_id> <html_file>
      PATCH the candidate's resume-summary field with the HTML in html_file.
      Refuses if the HTML contains an em dash.

API key resolution: env TEAMTAILOR_API_KEY, else parsed from
../../../teamtailor_flag.py (repo root), else --key.
"""
import sys, os, re, json, argparse, html as htmllib, subprocess, tempfile
import requests

BASE = "https://api.na.teamtailor.com"
VER = "20240904"

def get_key(cli_key=None):
    if cli_key: return cli_key
    k = os.environ.get("TEAMTAILOR_API_KEY")
    if k: return k
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "..", "..", "teamtailor_flag.py"),
        os.path.join(here, "..", "..", "..", "teamtailor_flag.py"),
        # absolute fallback so the skill works from any project (key already lives here)
        os.path.expanduser("~/Claude zinspector/teamtailor_flag.py"),
    ]
    for up in candidates:
        if os.path.exists(up):
            txt = open(up).read()
            m = re.search(r'os\.environ\.get\("TEAMTAILOR_API_KEY",\s*"([^"]+)"\)', txt)
            if m: return m.group(1)
    raise SystemExit("No TT API key. Set env TEAMTAILOR_API_KEY, or pass --key, "
                     "or keep teamtailor_flag.py at ~/Claude zinspector/.")

def H(key, write=False):
    h = {"Authorization": f"Token token={key}", "X-Api-Version": VER}
    if write: h["Content-Type"] = "application/vnd.api+json"
    return h

def strip_html(s):
    s = re.sub(r"<br\s*/?>", "\n", s or "")
    s = re.sub(r"</p>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return htmllib.unescape(s).replace("\xa0", " ").strip()

def parse_share_url(arg):
    """Return (candidate_id, share_url_or_None)."""
    m = re.search(r"/shares/[^/]+/(\d+)", arg)
    if m: return m.group(1), arg
    if arg.isdigit(): return arg, None
    m = re.search(r"/candidate/(\d+)", arg)
    if m: return m.group(1), None
    raise SystemExit(f"Cannot parse candidate id from: {arg}")

def fetch_transcript(share_url):
    if not share_url: return None
    r = requests.get(share_url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200: return None
    t = r.text
    # find the <summary>Transcript</summary> block, then the following div content
    m = re.search(r"<summary[^>]*>\s*Transcript\s*</summary>\s*<div[^>]*>(.*?)</div>", t, re.S | re.I)
    if not m:
        return None
    return strip_html(m.group(1))

def cv_text(candidate_attrs):
    url = candidate_attrs.get("resume")
    if not url: return ""
    try:
        pdf = requests.get(url, timeout=90).content
    except Exception:
        return ""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf); path = f.name
    text = ""
    try:
        out = subprocess.run(["pdftotext", path, "-"], capture_output=True, timeout=60)
        if out.returncode == 0: text = out.stdout.decode("utf-8", "ignore")
    except Exception:
        pass
    if not text.strip():
        try:
            from pypdf import PdfReader
        except ImportError:
            try: from PyPDF2 import PdfReader
            except ImportError: PdfReader = None
        if PdfReader:
            try:
                text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            except Exception:
                pass
    try: os.unlink(path)
    except Exception: pass
    return text.strip()

def trusted_fields(cid, key):
    r = requests.get(f"{BASE}/v1/candidates/{cid}",
                     headers=H(key), params={"include": "custom-field-values.custom-field"}, timeout=60)
    r.raise_for_status()
    j = r.json()
    a = j["data"]["attributes"]
    cfmap = {i["id"]: i["attributes"]["api-name"] for i in j.get("included", []) if i["type"] == "custom-fields"}
    fields = {}
    for i in j.get("included", []):
        if i["type"] == "custom-field-values":
            cf = i["relationships"]["custom-field"]["data"]["id"]
            name = cfmap.get(cf); val = i["attributes"].get("value")
            if isinstance(val, list): val = val[0] if val else None
            fields[name] = val
    return a, fields

def cmd_extract(args):
    key = get_key(args.key)
    cid, share = parse_share_url(args.target)
    attrs, fields = trusted_fields(cid, key)
    transcript = fetch_transcript(share) if share else None
    bundle = {
        "candidate_id": cid,
        "name": f"{attrs.get('first-name','')} {attrs.get('last-name','')}".strip(),
        "share_url": share,
        "english_level": fields.get("english-level"),      # trusted CEFR, e.g. "Advanced (C1)"
        "years_of_experience": fields.get("years-of-experience"),
        "salary_expectation": fields.get("salary-expectations"),
        "has_transcript": bool(transcript),
        "transcript": transcript or "",
        "cv_text": cv_text(attrs),
    }
    out = json.dumps(bundle, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w").write(out); print(f"[written {args.out}] has_transcript={bundle['has_transcript']} name={bundle['name']} english={bundle['english_level']}")
    else:
        print(out)

def cmd_write(args):
    key = get_key(args.key)
    html = open(args.html_file, encoding="utf-8").read()
    if "—" in html:
        raise SystemExit("ERROR: em dash (—) present in summary. Remove it before writing.")
    r = requests.patch(f"{BASE}/v1/candidates/{args.candidate_id}", headers=H(key, write=True),
                       data=json.dumps({"data": {"id": args.candidate_id, "type": "candidates",
                                                 "attributes": {"resume-summary": html}}}), timeout=60)
    print("PATCH", r.status_code, "OK" if r.status_code == 200 else r.text[:300])
    if r.status_code != 200: sys.exit(1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--key")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract"); e.add_argument("target"); e.add_argument("--out"); e.set_defaults(fn=cmd_extract)
    w = sub.add_parser("write"); w.add_argument("candidate_id"); w.add_argument("html_file"); w.set_defaults(fn=cmd_write)
    a = p.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
