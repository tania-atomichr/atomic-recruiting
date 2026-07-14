"""Enumerate EVERY screened candidate in the whole Teamtailor DB (not just one job's stage).

The `screened` flag is a candidate checkbox custom-field. The efficient way to list everyone
who has it is the custom-field-values endpoint filtered to that field, pulling the candidate
back with `include=owner` (NOT `include=candidate` — that 400s; the value's owner IS the
candidate). Two non-obvious gotchas, both learned the hard way:
  - the checkbox value is the STRING "true", never a boolean, so filter on == "true".
  - the owner candidate already carries `resume-summary`, so this single pass gets you the
    whole pool WITH the screening write-ups — no per-candidate call needed yet.

Output: work/screened.jsonl, one candidate per line:
  {id, name, summary, profile_url, email, tags}

Usage:
    python3 harvest_screened.py --out work/screened.jsonl
    python3 harvest_screened.py --out work/screened.jsonl --limit 60   # smoke test (~2 pages)
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tt_client import get_pages, get_one


def find_screened_field_id():
    fields, _ = get_pages("custom-fields")
    for f in fields:
        a = f["attributes"]
        if a.get("api-name") == "screened" or a.get("name", "").strip().lower() == "screened":
            return f["id"]
    raise SystemExit("No 'screened' custom-field found. Check GET /v1/custom-fields for its exact name.")


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/screened.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="stop after N values (smoke test)")
    args = ap.parse_args()

    fid = find_screened_field_id()
    print(f"screened field id: {fid}", file=sys.stderr)

    values, included = get_pages(
        "custom-field-values",
        {"filter[custom-field]": fid, "include": "owner"},
        cap=args.limit or None,
    )
    cands = {c["id"]: c for c in included if c["type"] == "candidates"}

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    kept = 0
    with out.open("w") as fh:
        for v in values:
            if str(v["attributes"].get("value")).lower() != "true":
                continue
            owner = v["relationships"].get("owner", {}).get("data")
            if not owner or owner["id"] not in cands:
                continue
            c = cands[owner["id"]]
            a = c["attributes"]
            rec = {
                "id": c["id"],
                "name": (a.get("first-name", "") + " " + a.get("last-name", "")).strip() or a.get("name", ""),
                "summary": strip_html(a.get("resume-summary", "")),
                "profile_url": a.get("profile-url", ""),
                "email": a.get("email", ""),
                "tags": a.get("tags", []),
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            kept += 1
    print(f"screened candidates written: {kept} -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
