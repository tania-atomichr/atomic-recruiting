#!/usr/bin/env python3
"""Deterministic fit-score from 7 dimension verdicts -- NO API, NO network.

You (the assistant) apply the rubric in RUBRIC.md and produce the 7 verdicts. This script
turns those verdicts into the SAME number the production app shows: weighted, with the
critical-gate caps, plus the evidence_type consistency + thin-data corrections. Extracted
verbatim from atomic-HR ranking.py.

Input: JSON (file arg, or stdin) = a list of exactly 7 items, in dimension order:
  [{"label": "Core skills", "status": "met|partial|unmet",
    "evidence": "short phrase from the profile",
    "evidence_type": "positive|negative|neutral"}, ...]
Optional: --profile-file / --profile so the thin-data guard can see how sparse the profile is.

  echo '[...verdicts...]' | python3 compute_score.py
  python3 compute_score.py verdicts.json --profile-file candidate.txt

Prints the 0-100 score and the (possibly corrected) breakdown.
"""
import re, json, sys, argparse
from typing import Optional

_DIM_WEIGHTS = {"core": 24, "seniority": 20, "domain": 14, "communication": 14,
                "environment": 12, "education": 8, "trajectory": 8}
_CRITICAL_DIMS = {"core", "seniority", "communication"}
_STATUS_VALUE = {"met": 1.0, "partial": 0.5, "unmet": 0.0}
_MISMATCH_RE = re.compile(
    r"(?:not |no |without |lacks? |missing |wrong |different |mismatch|"
    r"only (?:mobile|frontend|backend|data|marketing|sales|design)|"
    r"exclusively |none of |zero |doesn.t match|does not match|"
    r"unrelated|clearly |opposite )", re.I)
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def _correct_by_evidence_type(requirement_matches):
    """Enforce consistency between evidence_type and status.
    - PARTIAL + negative evidence_type → UNMET (real mismatch shouldn't be yellow)
    - UNMET + no evidence at all → PARTIAL (can't judge without data)
    - UNMET + neutral evidence_type → PARTIAL *only if* the evidence text reads
      as genuine silence (no data). If the text describes a real mismatch (wrong
      craft, different specialization) the LLM mislabeled it neutral — keep UNMET.
    """
    corrected = 0
    for r in (requirement_matches or []):
        if not isinstance(r, dict):
            continue
        status = (r.get("status") or "").strip().lower()
        et = (r.get("evidence_type") or "").strip().lower()
        label = (r.get("label") or "?")
        evidence = (r.get("evidence") or "").strip()
        if status == "unmet" and not et and not evidence:
            r["status"] = "partial"
            r["evidence"] = "[insufficient data to determine]"
            corrected += 1
            logging.info("[score] evidence_type correction: UNMET→PARTIAL on '%s' (no evidence at all)", label)
        elif status == "unmet" and et == "neutral":
            if _MISMATCH_RE.search(evidence):
                r["evidence_type"] = "negative"
                logging.info("[score] evidence_type fix: neutral→negative on '%s' (evidence describes mismatch)", label)
            else:
                r["status"] = "partial"
                corrected += 1
                logging.info("[score] evidence_type correction: UNMET→PARTIAL on '%s' (evidence_type=neutral, no mismatch language)", label)
        elif status == "partial" and et == "negative":
            r["status"] = "unmet"
            corrected += 1
            logging.info("[score] evidence_type correction: PARTIAL→UNMET on '%s' (evidence_type=negative)", label)
    return corrected


def _dim_key(label: str):
    l = (label or "").lower()
    if "core" in l or "skill" in l: return "core"
    if "senior" in l: return "seniority"
    if "environment" in l: return "environment"
    if "domain" in l or "industry" in l: return "domain"
    if "communication" in l or "market" in l or "language" in l: return "communication"
    if "education" in l or "degree" in l: return "education"
    if "trajectory" in l or "stability" in l: return "trajectory"
    return None


def _score_from_dimensions(requirement_matches, profile_text: str = "") -> Optional[int]:
    """Compute match_score (0-100) from the dimension verdicts. met=full weight, partial=half,
    unmet=0; normalized over the dimensions actually present.

    Corrections (in order):
    1. evidence_type check: if the LLM said UNMET but its own evidence_type is 'neutral'
       (no data either way), upgrade to PARTIAL — absence isn't disqualification.
    2. Thin-data guard: on sparse profiles, critical-dim UNMETs with neutral evidence_type
       are upgraded to PARTIAL, since the LLM can't reliably distinguish 'not mentioned'
       from 'doesn't meet' with so little text.

    Both use the LLM's evidence_type field (positive/negative/neutral) instead of regex.
    Returns None if the breakdown can't be mapped."""
    if not requirement_matches:
        return None
    _correct_by_evidence_type(requirement_matches)
    # THIN-DATA GUARD: on sparse profiles, even critical-dim UNMETs with neutral evidence
    # should be PARTIAL. The evidence_type correction above handles the general case; this
    # adds an extra layer for critical dims on thin profiles where the LLM might have said
    # evidence_type='negative' on very thin text that doesn't really support that judgment.
    pt = (profile_text or "").strip()
    year_markers = len(re.findall(r"\b(19|20)\d{2}\b", pt))
    thin = year_markers < 6 and len(pt) < 1200
    if thin:
        for r in (requirement_matches or []):
            if not isinstance(r, dict):
                continue
            k = _dim_key((r.get("label") or ""))
            et = (r.get("evidence_type") or "").strip().lower()
            if k in _CRITICAL_DIMS and (r.get("status") or "").strip().lower() == "unmet" and et != "negative":
                r["status"] = "partial"
                r["evidence_type"] = "neutral"
                logging.info("[score] thin-data guard: UNMET→PARTIAL on '%s' (thin profile, evidence_type was '%s')", r.get("label", "?"), et)
    by = {}
    for r in requirement_matches:
        k = _dim_key((r or {}).get("label"))
        if k and k not in by:
            by[k] = ((r or {}).get("status") or "").strip().lower()
    if len(by) < 5:
        return None
    total_w = sum(_DIM_WEIGHTS[k] for k in by)
    earned = sum(_DIM_WEIGHTS[k] * _STATUS_VALUE.get(by[k], 0.0) for k in by)
    score = round(earned / total_w * 100) if total_w else 0
    crit_unmet = sum(1 for k in _CRITICAL_DIMS if by.get(k) == "unmet")
    # Caps match the prompt guidance ("one gate unmet caps at 38, two at 24, three at 14")
    # and the smoke-gate invariant: a genuine critical-dim UNMET is never a 40+ score.
    if crit_unmet >= 3:   score = min(score, 14)
    elif crit_unmet == 2: score = min(score, 24)
    elif crit_unmet == 1: score = min(score, 38)
    return max(0, min(100, int(score)))



def main():
    ap = argparse.ArgumentParser(description="Compute the deterministic fit score from 7 verdicts (no API).")
    ap.add_argument("verdicts", nargs="?", help="JSON file of the 7 verdicts (else stdin)")
    ap.add_argument("--profile"); ap.add_argument("--profile-file")
    a = ap.parse_args()
    raw = open(a.verdicts, encoding="utf-8").read() if a.verdicts else sys.stdin.read()
    rm = json.loads(raw)
    if isinstance(rm, dict) and "requirementMatches" in rm:
        rm = rm["requirementMatches"]
    profile = a.profile or (open(a.profile_file, encoding="utf-8").read() if a.profile_file else "")
    score = _score_from_dimensions(rm, profile)   # mutates rm in place with corrections
    icon = {"met": "[MET]    ", "partial": "[PARTIAL]", "unmet": "[UNMET]  "}
    print(f"\n  MATCH SCORE: {score}/100\n")
    print("  7-DIMENSION BREAKDOWN (after consistency corrections):")
    for d in rm:
        st = (d.get("status") or "").lower()
        print(f"    {icon.get(st, '[?]      ')} {d.get('label'):<26} {d.get('evidence')}")
    crit = sum(1 for d in rm if (d.get('label','') .lower().split()[0] in ('core','real','communication')) )
    print()


if __name__ == "__main__":
    main()
