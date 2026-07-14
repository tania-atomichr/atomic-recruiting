#!/usr/bin/env python3
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
        ("\u2026", "..."), ("\u2018", "'"), ("\u2019", "'"),
        ("\u201c", '"'),  ("\u201d", '"'), ("\u2013", "-"),
        ("\u2014", "--"),  ("\u2022", "*"), ("\u00b7", "."),
        ("\u00a0", " "),   ("\u00ad", ""),
    ]:
        s = s.replace(src, dst)
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if ord(c) < 128)


# ====================================================================================
# RUBRIC CONSTANTS (verbatim from ranking.py) ========================================
# ====================================================================================
_SEVEN_DIM_RULES = (
    "STEP 0 — INTERPRET THE BRIEF FOR INTENT (do NOT take it literally or keyword-match). A brief is "
    "usually a raw pasted job description; read it the way an expert recruiter would and extract:\n"
    "  (a) CORE CRAFT — the function and skills the person actually performs. This is the PRIMARY axis: "
    "can this candidate DO the job? Judge craft before vertical.\n"
    "  (b) HIRING-COMPANY BUSINESS & ENVIRONMENT — first IDENTIFY the hiring company's OWN business "
    "model from its name and the JD's language: signals like 'book of business', 'our clients', "
    "'partners', 'accounts', 'agency', 'portfolio of clients' = a services/agency firm; a single "
    "product/brand/app = in-house product; many internal departments = enterprise. Judge the candidate's "
    "environment AND domain fit against the hiring company's OWN business — NOT the industries that "
    "company serves. (A marketing agency whose clients are universities is hiring an AGENCY paid-media "
    "operator, not a higher-ed specialist.)\n"
    "  (c) SERVED-VERTICAL vs REQUIRED-VERTICAL — CRITICAL, and the most common scoring mistake. "
    "Distinguish a vertical that appears only because it is the EMPLOYER'S market or client base "
    "(e.g. 'our clients are universities', 'drive enrollment growth', 'for the hospitality sector') — "
    "which is CONTEXT about the company, NEVER a candidate requirement — from a vertical the brief "
    "EXPLICITLY requires of the candidate ('must have N years IN the X industry'). An industry named as "
    "context, or as 'preferred/ideally', is NOT a gate: fully credit transferable experience from any "
    "adjacent revenue-/lead-/performance-driven industry, and never mark a strong-craft candidate down "
    "merely for coming from a different vertical.\n"
    "  (d) MUST-HAVE vs PREFERENCE — required/must/minimum/'X+ years'/hard constraints (language, "
    "location, work authorization) = GATES (a missing one can be UNMET). preferred/ideally/nice-to-have/"
    "a plus/bonus/familiarity = BOOSTS if present, NEVER a penalty if absent.\n"
    "  If the brief lists no explicit requirements, infer sensible must-haves from the core role and "
    "treat any niche vertical as transferable context, not a gate.\n"
    "  Judge whether the candidate can DO the job — not whether they mirror every noun in the post.\n\n"
    "HOW TO READ A WORK HISTORY (apply across ALL 7 dimensions — this is about PROCESSING the "
    "candidate fairly, not relaxing the requirements):\n"
    "  • READ DESCRIPTIONS, NOT JUST TITLES. A title often under- or over-states the real work — "
    "judge what the person ACTUALLY DID from the role description. A 'Customer Success Engineer' who "
    "ships SDKs, sample apps and custom implementations IS doing software engineering; credit the work "
    "EVIDENCED in the text, not the label.\n"
    "  • CAREER MOVES ARE BREADTH, NOT GAPS. Moving into product / management / lead roles and later "
    "back into hands-on engineering is GROWTH and added range — NOT a loss of craft or a 'recent gap'. "
    "Engineering (or any core) capability does not evaporate during a PM/PO/lead interlude, and a return "
    "to a senior IC/eng role re-demonstrates it. When the craft appears BEFORE and AFTER a detour, treat "
    "the whole arc as competent in that craft; weight the current/most-recent role first, but do NOT "
    "label someone 'no longer an engineer' for having grown through product or leadership.\n"
    "  • SILENCE IS NOT A NEGATIVE. Absence of a written description, or of a specific tool name, for a "
    "senior role at a clearly-relevant company is UNCERTAINTY — not evidence the skill is missing. Do "
    "NOT manufacture a penalty from what the profile simply didn't spell out: when the title, company, "
    "domain and trajectory make a capability likely, that is PARTIAL/unconfirmed, never UNMET.\n"
    "  • UNMET REQUIRES POSITIVE CONTRARY EVIDENCE — THIS IS THE SINGLE MOST IMPORTANT RULE. There is a "
    "hard difference between 'the profile PROVES this person does NOT fit' and 'the profile does not "
    "give us enough to confirm it'. The FIRST is UNMET. The SECOND is ALWAYS PARTIAL — never UNMET. "
    "Mark a dimension UNMET ONLY when something concretely present in the profile CONTRADICTS the "
    "requirement (e.g. brief needs 5+ yrs and the dated history shows 1; brief requires on-site in city X "
    "and they state remote-only elsewhere; brief needs backend and profile shows only mobile/frontend work). "
    "NOTE: a profile that shows a DIFFERENT specialization or craft than required IS contrary evidence — "
    "you can see what they do, and it's not what the brief needs. That is UNMET with evidence_type='negative', "
    "not PARTIAL. If the disqualifying fact is merely UNSTATED / not described / "
    "not spelled out, that is PARTIAL. 'No description confirms X', 'not evidenced', 'unclear', 'not "
    "mentioned' are PARTIAL phrasings — if your evidence sentence contains that kind of language, the "
    "status MUST be partial, not unmet.\n"
    "  • THIS MATTERS MOST FOR THE THREE GATE DIMENSIONS — Core skills (1), Real seniority (2), and "
    "Communication (5) — because an UNMET on these HARD-CAPS the entire score (one gate unmet caps at 38, "
    "two at 24, three at 14). So a wrongly-absence-based UNMET on any of these single-handedly tanks an "
    "otherwise-strong candidate. Before marking ANY of 1/2/5 unmet, require an explicit contradicting fact "
    "from the profile; if you only have absence/uncertainty, use PARTIAL. Specifically for Communication: a "
    "profile written in another language, or with no English certificate, is NOT English UNMET — employment "
    "by / delivery for a US or English-speaking company (per dimension 5's rules) is MET, and even without "
    "that, missing English proof is PARTIAL (unconfirmed), never UNMET.\n\n"
    "Then work through these 7 dimensions in order. Follow the stop/flag rules precisely.\n\n"
    "1. Core skills\n"
    "   Identify the must-have competencies for this search. Evaluate BOTH the craft/function AND "
    "evidence of the specific skills the brief requires.\n"
    "   → MET when the craft matches AND the profile shows evidence of the required skills (tools, "
    "projects, responsibilities described).\n"
    "   → PARTIAL when the craft matches and ONE OR A FEW specific skills are unconfirmed, but the "
    "role/company/domain make them plausible (a senior engineer at a relevant company with no tool list "
    "— partial, not unmet). Also PARTIAL when a title suggests the right craft but descriptions are thin.\n"
    "   → UNMET when the profile has been examined and shows NONE of the required core competencies — "
    "even if the title sounds right, zero evidence of the required skills across the whole profile is a "
    "real gap, not mere silence. A title alone does not confirm core skills when the brief asks for "
    "specific competencies and the profile shows no trace of any of them.\n"
    "   CRITICAL FOR CORE SKILLS: when the profile shows a DIFFERENT specialization than the brief "
    "requires (e.g. mobile dev when backend is needed, frontend when data-engineering is needed, "
    "marketing when sales is needed), that IS negative evidence — you HAVE data and it points AWAY "
    "from the requirement. Set evidence_type='negative' and status='unmet'. This is NOT silence or "
    "absence — the candidate's actual work is visible and it's the wrong craft.\n\n"
    "2. Real seniority\n"
    "   Count relevant years from when they ACTUALLY started doing this type of work "
    "(not from graduation, not from headline claims like '8 años'). "
    "Check whether the title's real scope matches what the search needs — "
    "leadership vs IC, team/budget size, decision-making authority — because the same title means "
    "very different things across companies. A move INTO product/management and back into a senior "
    "engineering role does NOT reset or erase the craft seniority — count the engineering years across "
    "the whole arc, and read a return to a staff/senior IC role as confirmation, not a fresh start.\n"
    "   A PRIOR LEADERSHIP TITLE IS POSITIVE EVIDENCE, NOT ABSENCE. If the history shows a real lead "
    "title (Tech Lead, Team Lead, Lead Engineer, EM, Staff), that title IS evidence the person has "
    "operated at that level — even when the profile gives NO description of the pod size / ownership / "
    "scope. Undescribed scope on a real lead title is UNCERTAINTY → at worst PARTIAL; it is NEVER 'no "
    "evidence of leadership'. Do not write 'no evidence of tech-lead scope' when a Tech-Lead/Team-Lead "
    "title is present — that is dismissing real evidence as if it were absent. A currently-IC person "
    "who held a lead title before still has demonstrated lead capability (MET or PARTIAL, per how "
    "recent/substantial it was), not UNMET.\n"
    "   → UNMET only if the person has NO lead title/experience anywhere AND the role hard-requires "
    "lead seniority, OR real counted years are clearly under the required level.\n"
    "   → PARTIAL if a lead title exists but is old/brief or its scope is undescribed/ambiguous.\n\n"
    "3. Environment fit\n"
    "   Map their experience to company type: product company vs agency/consulting vs enterprise; "
    "startup vs scale-up vs large corp. Match against what this client is.\n"
    "   WEIGHT RECENCY HEAVILY — judge by the RECENT years (roughly the last ~5) and the CURRENT/most-"
    "recent roles above all. Early-career consulting / freelance / contract / agency / founder work is "
    "NOT a penalty when the recent roles are in the right environment type: people legitimately start "
    "in consulting/contracting/their own venture and move into product, and that early stint says "
    "nothing about present fit. A brief's 'no consulting/freelance/founder-led' constraint means "
    "PREDOMINANTLY or RECENTLY that — never an old early-career engagement once recent roles match.\n"
    "   → MET if the current/recent roles match the target environment, even with older mismatched "
    "(consulting/freelance/founder) work.\n"
    "   → UNMET only if the RECENT and PREDOMINANT experience is in a clearly mismatched environment, "
    "or real time in the right environment type is too short.\n\n"
    "4. Domain / industry alignment\n"
    "   This dimension evaluates INDUSTRY and VERTICAL — NOT skills or tools (that was dimension 1). "
    "Ask: has this person worked in the same or an adjacent industry/market/vertical as the hiring "
    "company? Examples of domain: B2B SaaS, fintech, e-commerce, pharma, edtech, real estate, "
    "hospitality, healthcare, media, advertising/agency. Judge the BUSINESS CONTEXT they've operated "
    "in, not whether they know specific technologies.\n"
    "   Remember the Step 0 rules: identify the HIRING COMPANY'S own business first (product vs "
    "agency vs enterprise), then judge domain fit against THAT — not against the industries it serves. "
    "A vertical named only as preferred/ideally is never a penalty.\n"
    "   → MET when their recent work is in the same or closely adjacent vertical (e.g. B2B SaaS → "
    "B2B fintech, or e-commerce → retail tech — same market dynamics, similar buyers/users).\n"
    "   → PARTIAL when the vertical is different but has transferable business context (e.g. enterprise "
    "pharma → enterprise SaaS — both are large-org B2B, different product domain), OR when the brief's "
    "domain requirement is only preferred/nice-to-have.\n"
    "   → UNMET only when the domain is a hard requirement AND the person's industry background is "
    "clearly unrelated with no adjacent overlap (e.g. hospitality operations → compliance fintech).\n\n"
    "5. Communication & market fit\n"
    "   Check what the search requires (language level, working with US/foreign teams, "
    "timezone, on-site vs remote). Confirm actual EVIDENCE — ANY of the following counts as MET "
    "(do NOT demand a certificate when other evidence is present):\n"
    "   • Worked in the target language/market — managed US/foreign campaigns, led a cross-border team, "
    "OR was EMPLOYED BY / delivered work for a US-based or English-speaking company or agency "
    "(including a remote role for a US company). For LATAM talent serving US clients this is the norm "
    "and is strong evidence of working English.\n"
    "   • The candidate's own resume / LinkedIn profile is written in fluent, professional English — a "
    "full, correctly-written English profile IS evidence of working proficiency (different from merely "
    "listing 'English: Advanced' as a skill, which alone is NOT evidence).\n"
    "   • Language certification (TOEFL iBT ≥100 / IELTS ≥7.0 = strong; TOEFL 80-99 / IELTS 6.0-6.5 = "
    "functional), OR a degree / extended study conducted in the target language.\n"
    "   → PARTIAL only if signals are weak or ambiguous; → UNMET only if a hard language requirement has "
    "NO supporting evidence of any kind. Do not mark down a candidate who has clear US-company/agency experience.\n\n"
    "6. Education\n"
    "   Evaluate whether the candidate's education ALIGNS with what this role needs — "
    "field relevance matters, not just the presence of a degree.\n"
    "   → MET: degree field is directly relevant to the role domain "
    "(e.g. Marketing/Communications/Business for a marketing role; CS/Engineering for a technical role)\n"
    "   → PARTIAL: has a degree or credential but in an unrelated field — "
    "note both what they have AND how far it is from the role's domain\n"
    "   → UNMET: no education listed on the profile, OR the brief requires a specific "
    "degree or certification that is not evidenced\n"
    "   Even when education is not a stated requirement, an unrelated degree is PARTIAL not MET.\n\n"
    "7. Trajectory & stability\n"
    "   Judge RECENT trajectory (roughly the last 5 years) — old history barely matters once recent "
    "tenure is solid. Check for: job-hop pattern (more than 3 employers in the last 5 years), an "
    "unexplained RECENT gap > 3 months, backwards moves in seniority, or vague self-employment as the "
    "only recent evidence of work.\n"
    "   → MET if recent tenures are reasonably long and continuous — even if there is an OLD gap or a "
    "short stint years ago. Do NOT penalize gaps older than ~3 years when recent history is stable.\n"
    "   → PARTIAL only for a genuine RECENT instability signal (borderline hopping, or a recent "
    "unexplained gap with no clear reason).\n"
    "   → UNMET if RECENT job-hopping is clear (>3 employers / 5 yrs) or recent gaps are unexplained.\n\n"
)

_CHANGE_SIGNALS_RULES = (
    "After the 7 dimensions, scan for OPENNESS-TO-CHANGE signals. "
    "Only report signals that are actually evidenced in the profile text — do not invent them.\n"
    "Signals to look for (ranked roughly strongest → weakest):\n"
    "• 'Open to Work' badge — green ring on photo, 'Open to work' in headline or About [STRONG]\n"
    "• Recent title regression or lateral move — latest entry shows a step back or sideways "
    "(Manager → IC, Lead → Engineer) which often signals dissatisfaction [STRONG]\n"
    "• Just returned from a career break — a gap in Experience followed by a recent re-entry [STRONG]\n"
    "• Flat title / no internal promotion — same title in the same company for 3+ years "
    "with no stacked title change (common push factor) [MODERATE]\n"
    "• Recent side project or freelance overlapping current job — "
    "an Experience entry that started while the current role is still active [MODERATE]\n"
    "• Past tenure pattern — average tenure across all past roles; "
    "if they've historically moved every ~2–3 years and are now at or past that mark, flag it [MODERATE]\n"
    "• Time in current role ≥ 3 years — do the date math on the most recent Experience entry [MODERATE]\n"
    "• Recent certification or degree in the last ~12 months — "
    "a fresh Licenses & Certifications or Education entry (self-investment before a move) [WEAK]\n"
    "• Profile written in English for a LATAM candidate — English headline/About/descriptions "
    "signal positioning for the international market [WEAK — most active candidates do this]\n"
    "• Recent LinkedIn activity — any post, comment, or reaction timestamped within ~30 days "
    "(they are active on the platform and will see messages) [WEAK — activity alone does not mean open]\n\n"
    "Return found signals as short, specific phrases (e.g. '3.5 yrs in current role, past their 2-yr avg'). "
    "Only include WEAK signals if at least one MODERATE or STRONG signal is also present. "
    "Return an EMPTY array [] if no real signals are evidenced. Do NOT fabricate.\n\n"
    "Then set openness_pct using this calibration (most people are NOT actively looking — default low):\n"
    "  0–15 = no signals; recently promoted or clearly growing in current role\n"
    " 16–30 = 1 weak signal only (e.g. 3 yrs in role but otherwise stable and progressing)\n"
    " 31–50 = 2–3 soft signals (tenure milestone + flat title + maybe activity); plausible but not urgent\n"
    " 51–70 = strong push factors — flat title for years, tenure past their own historical average, OR side project\n"
    " 71–90 = multiple strong signals — regression/lateral move, career-break re-entry, OR OtW badge + other signals\n"
    " 91–100 = explicit Open to Work badge AND multiple strong push factors\n"
    "Weak signals (English profile, LinkedIn activity) must NOT push the score above 40 on their own.\n\n"
)

_REQ_MATCHES_SPEC = (
    '- "requirementMatches": array of EXACTLY 7 items, one per dimension above (in order).\n'
    '  Each item: {"label": dimension name (e.g. "Core skills"), '
    '"status": "met"|"partial"|"unmet", '
    '"evidence": one short phrase of real evidence from THIS profile — '
    'never "not evidenced", instead describe what IS or IS NOT shown, '
    '"evidence_type": "positive"|"negative"|"neutral" — '
    'classify what the evidence SAYS. This is critical — status and evidence_type must be consistent:\n'
    '  "positive" = profile shows facts SUPPORTING this requirement.\n'
    '  "negative" = profile shows facts that CONTRADICT this requirement. '
    'Examples: wrong craft/specialization (mobile dev when backend needed, frontend when data-eng '
    'needed), wrong environment type (enterprise when startup needed), wrong industry/vertical '
    '(pharma when B2B SaaS needed), insufficient years, mismatched seniority direction. '
    "IMPORTANT: knowing someone's craft/industry and it being WRONG is negative, not neutral — "
    'you HAVE data and it doesn\'t match. "Mobile dev, not backend" is negative. '
    '"Pharma, not SaaS" is negative. '
    '"No industry info on profile" is neutral.\n'
    '  "neutral" = profile genuinely LACKS information to judge — you cannot tell either way.\n'
    '  Consistency rule: if evidence_type is "negative", status must be "unmet" (not "partial"). '
    'If evidence_type is "positive", status must be "met" (or "partial" if the match is weak)}.\n'
)



# ====================================================================================
# DETERMINISTIC SCORING (verbatim from ranking.py) ===================================
# ====================================================================================
_DIM_WEIGHTS = {"core": 24, "seniority": 20, "domain": 14, "communication": 14,
                "environment": 12, "education": 8, "trajectory": 8}
_CRITICAL_DIMS = {"core", "seniority", "communication"}
_STATUS_VALUE = {"met": 1.0, "partial": 0.5, "unmet": 0.0}
_MISMATCH_RE = re.compile(
    r"(?:not |no |without |lacks? |missing |wrong |different |mismatch|"
    r"only (?:mobile|frontend|backend|data|marketing|sales|design)|"
    r"exclusively |none of |zero |doesn.t match|does not match|"
    r"unrelated|clearly |opposite )", re.I)
_EXP_LINE_RE = re.compile(
    r"\b\d{4}\s*[-–—]\s*(?:\d{4}|present|actual)", re.IGNORECASE
)

def _profile_sufficient(profile_text: str) -> bool:
    """SYSTEMIC data-sufficiency gate. A profile must carry enough to actually evaluate the 7
    dimensions (real experience, seniority, education, trajectory). A bare headline / Sales-Nav
    stub of a few hundred chars CANNOT be scored honestly — scoring it invents a number (this is
    how a 209-char profile scored 82). Returns False for such stubs so every scoring path flags
    'needs profile data' instead of fabricating a score. Conservative threshold so a concise but
    complete profile (which has dated roles) still passes."""
    t = re.sub(r"\s+", " ", (profile_text or "").strip())
    if len(t) < 400:
        return False
    has_role_dates = bool(re.search(r"\b(19|20)\d{2}\b", t))   # experience entries carry years
    return has_role_dates or len(t) >= 800

def _insufficient_result() -> dict:
    return {"match_score": None, "insufficient_data": True,
            "why": "Profile data is incomplete — open this candidate in the extension to capture the "
                   "full profile, then it will score against the brief.",
            "gaps": "Not enough profile text to evaluate the 7 dimensions.",
            "requirementMatches": [], "change_signals": [], "openness_pct": None}

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
        "is an AGENCY -- its served vertical is context, not a candidate requirement).\n\n"
        f"BRIEF:\n{_to_ascii(b)[:4000]}\n\n"
        "Return ONLY JSON:\n"
        '{"hiring_company_business": "short phrase e.g. performance marketing agency",\n'
        ' "core_craft": "the function/skills the hire actually performs",\n'
        ' "strong_fit_backgrounds": ["4-8 candidate backgrounds/industries that transfer well -- '
        'include the company\'s own type plus adjacent verticals where the same craft applies"],\n'
        ' "bonus_not_required": ["nice-to-have backgrounds/verticals, e.g. the served vertical"]}'
    )
    try:
        text = _call_anthropic(prompt, None, FRAME_MODEL, 500)
        m = re.search(r"\{.*\}", text, re.DOTALL)
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
         "and dimension 4 Domain):\n")
    if biz:    g += f"- Hiring company's business: {biz}. Score environment/domain against THIS, not the industries it serves.\n"
    if craft:  g += f"- Core craft to score on: {craft}.\n"
    if strong: g += f"- STRONG-FIT backgrounds -- treat ANY of these as a domain MATCH (MET), not a gap: {', '.join(strong[:8])}.\n"
    if bonus:  g += f"- Bonus only -- nice-to-have, NEVER a penalty if absent: {', '.join(bonus[:6])}.\n"
    return g


def build_fit_prompt_parts(brief: str, profile: str, guidance: str, today_str: str):
    """THE canonical 7-dimension fit-scoring prompt (verbatim structure from ranking.py).
    company_stack_hint is omitted (DB-mined; "" for most profiles)."""
    system = (
        f"You are an expert recruiting assistant. A recruiter is sourcing for:\n\n"
        f'"{_to_ascii(brief)}"\n\n'
        + (guidance + "\n" if guidance else "")
        + f"Assess this candidate against the role using 7 standard dimensions.\n\n"
        + _SEVEN_DIM_RULES
        + _CHANGE_SIGNALS_RULES +
        f"Return ONLY a JSON object with these keys:\n"
        f'- "match_score": integer 0-100. '
        f'All dimensions MET -> 75-100; some PARTIAL -> 50-75; one critical UNMET -> at most 38; '
        f'multiple critical UNMETs -> below 25. Remember: UNMET requires POSITIVE CONTRARY EVIDENCE '
        f'from the profile -- absence/silence/uncertainty is always PARTIAL, never UNMET.\n'
        f'- "why": 2 sentences max on overall fit, citing specifics from the profile\n'
        f'- "gaps": one sentence on the most critical concern, or null if clean\n'
        + _REQ_MATCHES_SPEC +
        f'  The count of "met" items should reconcile with match_score.\n'
        f'- "change_signals": array of strings, one per found openness signal, or [] if none.\n'
        f'- "openness_pct": integer 0-100 per the calibration above.'
    )
    user = (
        f"Today's date is {today_str}. Use this when calculating time in role and tenure durations.\n\n"
        + f"PROFILE:\n{profile[:8000]}"
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
    m = re.search(r"\{.*\}", text, re.DOTALL)
    data = json.loads(m.group(0) if m else text)
    cs = [s for s in (data.get("change_signals") or []) if isinstance(s, str) and s.strip()]
    op = data.get("openness_pct")
    op = max(0, min(100, int(op))) if isinstance(op, (int, float)) else None
    rm = data.get("requirementMatches", [])
    computed = _score_from_dimensions(rm, profile)
    ms = computed if computed is not None else data.get("match_score")
    return {"match_score": ms, "why": data.get("why"), "gaps": data.get("gaps"),
            "requirementMatches": rm, "change_signals": cs, "openness_pct": op}


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
        print("\n  INSUFFICIENT DATA -- " + r["why"]); return
    print(f"\n  MATCH SCORE: {r['match_score']}/100")
    print(f"  Why:  {r.get('why')}")
    print(f"  Gaps: {r.get('gaps')}")
    print(f"  Openness: {r.get('openness_pct')}%")
    if r.get("change_signals"):
        print("  Change signals: " + "; ".join(r["change_signals"]))
    print("\n  7-DIMENSION BREAKDOWN:")
    icon = {"met": "[MET]    ", "partial": "[PARTIAL]", "unmet": "[UNMET]  "}
    for d in r.get("requirementMatches", []):
        st = (d.get("status") or "").lower()
        print(f"    {icon.get(st, '[?]      ')} {d.get('label'):<26} {d.get('evidence')}")
    print()


if __name__ == "__main__":
    main()
