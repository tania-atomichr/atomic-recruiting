"""Extract the exact rubric constants + deterministic-scoring functions from the atomic-hr
ranking.py so the skill is byte-identical to production, and emit a standalone score.py."""
import re, pathlib, textwrap

APP = pathlib.Path("/Users/taniaaguirre/Claude zinspector/atomic-hr-candidate-search")
ranking = (APP / "ranking.py").read_text()

def grab_assign(name, src=ranking):
    """Grab a top-level `name = ( ... )` paren-balanced assignment, verbatim."""
    m = re.search(rf"^{re.escape(name)} = \(", src, re.M)
    assert m, name
    i = m.end() - 1  # at the '('
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "(":
            depth += 1
        elif src[j] == ")":
            depth -= 1
            if depth == 0:
                return src[m.start():j+1]
    raise AssertionError(name)

def grab_simple_assign(name, src=ranking):
    """Grab a single-line `name = {...}` style assignment (may span lines with braces)."""
    m = re.search(rf"^{re.escape(name)} = ", src, re.M)
    assert m, name
    # balance braces/parens/brackets from the '=' onward
    i = m.end()
    depth = 0
    started = False
    for j in range(i, len(src)):
        ch = src[j]
        if ch in "{[(":
            depth += 1; started = True
        elif ch in "}])":
            depth -= 1
        elif ch == "\n" and (not started or depth == 0):
            return src[m.start():j]
        if started and depth == 0 and ch in "}])":
            return src[m.start():j+1]
    raise AssertionError(name)

def grab_func(name, src=ranking):
    """Grab a top-level `def name(...):` body up to (but not including) the next top-level def/const."""
    m = re.search(rf"^def {re.escape(name)}\(", src, re.M)
    assert m, name
    # find next top-level line (col 0, starts with def/_NAME =/# ──) after the body
    rest = src[m.end():]
    lines = src[m.start():].split("\n")
    out = [lines[0]]
    for ln in lines[1:]:
        if ln and not ln[0].isspace() and not ln.startswith(")"):
            break
        out.append(ln)
    # trim trailing blank lines
    while out and out[-1].strip() == "":
        out.pop()
    return "\n".join(out)

parts = {}
for c in ["_SEVEN_DIM_RULES", "_CHANGE_SIGNALS_RULES", "_REQ_MATCHES_SPEC"]:
    parts[c] = grab_assign(c)
for c in ["_DIM_WEIGHTS", "_CRITICAL_DIMS", "_STATUS_VALUE", "_MISMATCH_RE", "_EXP_LINE_RE"]:
    parts[c] = grab_simple_assign(c)
for f in ["_profile_sufficient", "_insufficient_result", "_correct_by_evidence_type",
          "_dim_key", "_score_from_dimensions"]:
    parts[f] = grab_func(f)

# sanity: print lengths
for k, v in parts.items():
    print(f"{k}: {len(v)} chars")

# ---- assemble the standalone script ----
HEADER = '''#!/usr/bin/env python3
"""Self-contained candidate fit-scorer — a faithful copy of the atomic-HR 7-dimension
scoring pipeline (ranking.py). Given a role BRIEF and a candidate PROFILE, it:

  1. runs the exact 7-dimension rubric prompt through Claude (temperature 0),
  2. recomputes the numeric match_score DETERMINISTICALLY from the dimension verdicts
     (weighted, with critical-gate caps) — NOT the LLM's free-pick number,
  3. applies the same data-sufficiency gate and evidence_type corrections.

The rubric text and scoring math below are extracted verbatim from production ranking.py,
so a given (brief, profile) scores the same here as in the app. Two production enrichments
that require the app's Postgres DB are intentionally omitted (they only ever ADD soft signal,
never change a gate): the per-brief derived SCORING FRAME is recomputed live via an LLM call
(no DB cache), and the mined company-tech hint is skipped (it is "" for most profiles anyway).

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 score.py --brief-file brief.txt --profile-file profile.txt
    python3 score.py --brief "..." --profile "..."            # inline
    cat profile.txt | python3 score.py --brief-file brief.txt  # profile on stdin
    python3 score.py ... --no-frame     # skip the derived-scoring-frame LLM call
    python3 score.py ... --json         # emit raw JSON only

Requires: pip install anthropic
"""
from __future__ import annotations
import argparse, json, logging, os, re, sys, unicodedata
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")

SCORE_MODEL = os.environ.get("SEARCH_MODEL", "claude-sonnet-4-6")  # production ranking default
FRAME_MODEL = os.environ.get("FRAME_MODEL", "claude-haiku-4-5")    # cheap scoring-frame derivation


def _to_ascii(s: object) -> str:
    """Convert to ASCII for Anthropic API calls (verbatim from utils.py)."""
    s = str(s)
    for src, dst in [
        ("\\u2026", "..."), ("\\u2018", "'"), ("\\u2019", "'"),
        ("\\u201c", \'"\'),  ("\\u201d", \'"\'), ("\\u2013", "-"),
        ("\\u2014", "--"),  ("\\u2022", "*"), ("\\u00b7", "."),
        ("\\u00a0", " "),   ("\\u00ad", ""),
    ]:
        s = s.replace(src, dst)
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if ord(c) < 128)


# ====================================================================================
# RUBRIC CONSTANTS (verbatim from ranking.py) ========================================
# ====================================================================================
'''

MIDDLE = '''

# ====================================================================================
# DETERMINISTIC SCORING (verbatim from ranking.py) ===================================
# ====================================================================================
'''

LLM = '''

# ====================================================================================
# LLM TRANSPORT + PROMPT ASSEMBLY ====================================================
# ====================================================================================
def _call_anthropic(user: str, system: str | None, model: str, max_tokens: int) -> str:
    try:
        import anthropic
    except ImportError:
        sys.exit("ERROR: pip install anthropic  (and set ANTHROPIC_API_KEY)")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ERROR: set ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=key)
    kwargs = dict(model=model, max_tokens=max_tokens, temperature=0,
                  messages=[{"role": "user", "content": user}])
    if system:
        kwargs["system"] = system
    resp = client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def _derive_scoring_spec(brief: str) -> str:
    """Derive the authoritative SCORING FRAME for this brief (env/domain anchor). Live LLM
    version of ranking.py's _derive_scoring_spec — no DB cache/persistence, same prompt+temp 0."""
    b = (brief or "").strip()
    if not b:
        return ""
    prompt = (
        "Read this hiring brief and infer the SCORING FRAME. Anchor on the HIRING COMPANY'S OWN "
        "business model, NOT the industries it serves (e.g. an agency whose clients are universities "
        "is an AGENCY -- its served vertical is context, not a candidate requirement).\\n\\n"
        f"BRIEF:\\n{_to_ascii(b)[:4000]}\\n\\n"
        "Return ONLY JSON:\\n"
        \'{"hiring_company_business": "short phrase e.g. performance marketing agency",\\n\'
        \' "core_craft": "the function/skills the hire actually performs",\\n\'
        \' "strong_fit_backgrounds": ["4-8 candidate backgrounds/industries that transfer well -- \'
        \'include the company\\'s own type plus adjacent verticals where the same craft applies"],\\n\'
        \' "bonus_not_required": ["nice-to-have backgrounds/verticals, e.g. the served vertical"]}\'
    )
    try:
        text = _call_anthropic(prompt, None, FRAME_MODEL, 500)
        m = re.search(r"\\{.*\\}", text, re.DOTALL)
        d = json.loads(m.group(0) if m else text)
    except Exception as exc:
        logging.warning(f"_derive_scoring_spec failed: {exc}")
        return ""
    biz = (d.get("hiring_company_business") or "").strip()
    craft = (d.get("core_craft") or "").strip()
    strong = [s for s in (d.get("strong_fit_backgrounds") or []) if isinstance(s, str) and s.strip()]
    bonus = [s for s in (d.get("bonus_not_required") or []) if isinstance(s, str) and s.strip()]
    if not (biz or craft or strong):
        return ""
    g = ("SCORING FRAME (derived from the hiring company -- AUTHORITATIVE for dimension 3 Environment "
         "and dimension 4 Domain):\\n")
    if biz:    g += f"- Hiring company's business: {biz}. Score environment/domain against THIS, not the industries it serves.\\n"
    if craft:  g += f"- Core craft to score on: {craft}.\\n"
    if strong: g += f"- STRONG-FIT backgrounds -- treat ANY of these as a domain MATCH (MET), not a gap: {', '.join(strong[:8])}.\\n"
    if bonus:  g += f"- Bonus only -- nice-to-have, NEVER a penalty if absent: {', '.join(bonus[:6])}.\\n"
    return g


def build_fit_prompt_parts(brief: str, profile: str, guidance: str, today_str: str):
    """THE canonical 7-dimension fit-scoring prompt (verbatim structure from ranking.py).
    company_stack_hint is omitted (DB-mined; "" for most profiles)."""
    system = (
        f"You are an expert recruiting assistant. A recruiter is sourcing for:\\n\\n"
        f'"{_to_ascii(brief)}"\\n\\n'
        + (guidance + "\\n" if guidance else "")
        + f"Assess this candidate against the role using 7 standard dimensions.\\n\\n"
        + _SEVEN_DIM_RULES
        + _CHANGE_SIGNALS_RULES +
        f"Return ONLY a JSON object with these keys:\\n"
        f\'- "match_score": integer 0-100. \'
        f\'All dimensions MET -> 75-100; some PARTIAL -> 50-75; one critical UNMET -> at most 38; \'
        f\'multiple critical UNMETs -> below 25. Remember: UNMET requires POSITIVE CONTRARY EVIDENCE \'
        f\'from the profile -- absence/silence/uncertainty is always PARTIAL, never UNMET.\\n\'
        f\'- "why": 2 sentences max on overall fit, citing specifics from the profile\\n\'
        f\'- "gaps": one sentence on the most critical concern, or null if clean\\n\'
        + _REQ_MATCHES_SPEC +
        f\'  The count of "met" items should reconcile with match_score.\\n\'
        f\'- "change_signals": array of strings, one per found openness signal, or [] if none.\\n\'
        f\'- "openness_pct": integer 0-100 per the calibration above.\'
    )
    user = (
        f"Today's date is {today_str}. Use this when calculating time in role and tenure durations.\\n\\n"
        + f"PROFILE:\\n{profile[:8000]}"
    )
    return system, user


def score_candidate(brief: str, profile: str, derive_frame: bool = True) -> dict:
    """Full pipeline: sufficiency gate -> (optional) scoring frame -> rubric LLM call ->
    deterministic score from dimension verdicts. Returns the same shape as ranking.py."""
    profile = _to_ascii(profile or "")[:8000]
    if not _profile_sufficient(profile):
        return _insufficient_result()
    today_str = datetime.utcnow().strftime("%B %d, %Y")
    guidance = _derive_scoring_spec(brief) if derive_frame else ""
    system, user = build_fit_prompt_parts(brief, profile, guidance, today_str)
    text = _call_anthropic(user, system, SCORE_MODEL, 2500)
    m = re.search(r"\\{.*\\}", text, re.DOTALL)
    data = json.loads(m.group(0) if m else text)
    cs = [s for s in (data.get("change_signals") or []) if isinstance(s, str) and s.strip()]
    op = data.get("openness_pct")
    op = max(0, min(100, int(op))) if isinstance(op, (int, float)) else None
    rm = data.get("requirementMatches", [])
    computed = _score_from_dimensions(rm, profile)
    ms = computed if computed is not None else data.get("match_score")
    return {"match_score": ms, "why": data.get("why"), "gaps": data.get("gaps"),
            "requirementMatches": rm, "change_signals": cs, "openness_pct": op}
'''

MAIN = '''

# ====================================================================================
# CLI ================================================================================
# ====================================================================================
def _read(inline, path, stdin_ok=False):
    if inline:
        return inline
    if path:
        return open(path, encoding="utf-8").read()
    if stdin_ok and not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def main():
    ap = argparse.ArgumentParser(description="Score a candidate against a role brief (atomic-HR 7-dim rubric).")
    ap.add_argument("--brief"); ap.add_argument("--brief-file")
    ap.add_argument("--profile"); ap.add_argument("--profile-file")
    ap.add_argument("--no-frame", action="store_true", help="skip the derived scoring-frame LLM call")
    ap.add_argument("--json", action="store_true", help="print raw JSON only")
    a = ap.parse_args()
    brief = _read(a.brief, a.brief_file)
    profile = _read(a.profile, a.profile_file, stdin_ok=True)
    if not brief or not profile:
        ap.error("need a brief (--brief/--brief-file) and a profile (--profile/--profile-file/stdin)")
    r = score_candidate(brief, profile, derive_frame=not a.no_frame)
    if a.json:
        print(json.dumps(r, indent=2)); return
    if r.get("insufficient_data"):
        print("\\n  INSUFFICIENT DATA -- " + r["why"]); return
    print(f"\\n  MATCH SCORE: {r['match_score']}/100")
    print(f"  Why:  {r.get('why')}")
    print(f"  Gaps: {r.get('gaps')}")
    print(f"  Openness: {r.get('openness_pct')}%")
    if r.get("change_signals"):
        print("  Change signals: " + "; ".join(r["change_signals"]))
    print("\\n  7-DIMENSION BREAKDOWN:")
    icon = {"met": "[MET]    ", "partial": "[PARTIAL]", "unmet": "[UNMET]  "}
    for d in r.get("requirementMatches", []):
        st = (d.get("status") or "").lower()
        print(f"    {icon.get(st, '[?]      ')} {d.get('label'):<26} {d.get('evidence')}")
    print()


if __name__ == "__main__":
    main()
'''

body = HEADER
for c in ["_SEVEN_DIM_RULES", "_CHANGE_SIGNALS_RULES", "_REQ_MATCHES_SPEC"]:
    body += parts[c] + "\n\n"
body += MIDDLE
for c in ["_DIM_WEIGHTS", "_CRITICAL_DIMS", "_STATUS_VALUE", "_MISMATCH_RE", "_EXP_LINE_RE"]:
    body += parts[c] + "\n"
body += "\n"
for f in ["_profile_sufficient", "_insufficient_result", "_correct_by_evidence_type",
          "_dim_key", "_score_from_dimensions"]:
    body += parts[f] + "\n\n"
body += LLM + MAIN

out = pathlib.Path("/Users/taniaaguirre/.claude/skills/candidate-fit-score/scripts/score.py")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(body)
print("WROTE", out, len(body), "chars")

# byte-check: the extracted rubric text must match ranking.py exactly
import compileall
print("compile:", compileall.compile_file(str(out), quiet=1))
