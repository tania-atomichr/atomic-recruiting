---
name: candidate-fit-score
description: Score a candidate against a role brief using atomic-HR's exact 7-dimension fit rubric (core skills, seniority, environment, domain, communication, education, trajectory), returning a 0-100 match score, a MET/PARTIAL/UNMET breakdown, gaps, and openness-to-change signals. Use when the user shares a candidate profile/CV/LinkedIn text plus a job brief and asks to score, evaluate, rank, or assess fit — or wants to know why a candidate does or doesn't fit a role.
---

# Candidate Fit Score (atomic-HR 7-dimension rubric)

Evaluate a candidate against a role **in this conversation**, using the same rubric and scoring
math as the production atomic-HR search app (`ranking.py`). **You (the assistant) apply the
rubric yourself** — no API call. A tiny local script turns your verdicts into the exact number
the production app would show, so the score is reproducible instead of an eyeballed guess.

## Inputs
- **Brief** — the role's job description / requirements (raw pasted JD is fine).
- **Profile** — the candidate's CV / LinkedIn / résumé text.

If either is missing, ask for it. If the profile is a bare stub (under ~400 chars, or no dated
roles), **do not score** — say it's insufficient data and ask for the full profile (this is the
production data-sufficiency gate; a thin profile makes any number fabricated).

## Workflow (per candidate)

1. **Read `RUBRIC.md`** (in this skill folder) — it is the exact, verbatim instruction text the
   production scorer uses: Step-0 brief interpretation, the "how to read a work history" rules,
   and the 7 dimensions with their MET/PARTIAL/UNMET definitions, plus the openness-signal scan.

2. **(Optional but recommended) Derive the SCORING FRAME first.** Before scoring, infer from the
   brief: the *hiring company's own business* (product vs agency vs enterprise — NOT the industries
   it serves), the core craft, and 4–8 strong-fit backgrounds that transfer. Anchor dimensions 3
   (Environment) and 4 (Domain) on that. This mirrors the app's derived scoring frame and prevents
   the most common mistake — penalizing a strong-craft candidate for coming from the "wrong" vertical
   when that vertical was only the employer's client base.

3. **Apply the rubric** to produce a verdict for each of the **7 dimensions in order**:
   Core skills · Real seniority · Environment fit · Domain/industry · Communication & market fit ·
   Education · Trajectory & stability. For each, decide `status` (met/partial/unmet), a one-phrase
   `evidence` from the profile, and `evidence_type` (positive/negative/neutral).

   **The doctrine that governs every verdict:** UNMET requires *positive contrary evidence* in the
   profile. Silence / "not mentioned" / uncertainty is **always PARTIAL, never UNMET**. A *different*
   craft or specialization than the brief needs IS contrary evidence → `evidence_type:"negative"` →
   UNMET. Read descriptions not titles; don't reset seniority for a PM/lead detour; weight recent
   years. (Full rules in `RUBRIC.md` — follow them, don't summarize from memory.)

4. **Compute the number** — write the 7 verdicts to a JSON array and run:
   ```bash
   echo '[{"label":"Core skills","status":"...","evidence":"...","evidence_type":"..."}, ...7...]' \
     | python3 ~/.claude/skills/candidate-fit-score/scripts/compute_score.py --profile-file profile.txt
   ```
   (or pass a file: `compute_score.py verdicts.json --profile-file profile.txt`). This applies the
   production weights, the **critical-gate caps** (core/seniority/communication: 1 UNMET→cap 38,
   2→cap 24, 3→cap 14), and the consistency corrections — then prints the 0-100 score. **Use this
   number; don't compute the weighted score by hand.**

5. **Also produce** (yourself, from the rubric): a 2-sentence `why`, a one-sentence `gaps` (or none),
   the `change_signals` array, and `openness_pct` (0-100) per the calibration in `RUBRIC.md`.

6. **Present**: the score, the 7-line MET/PARTIAL/UNMET breakdown (the script prints this), then
   why / gaps / openness. For several candidates, score each and rank by the number.

## Why the number is computed, not free-picked

The whole point of the production design: the LLM judges each *dimension*, but the *score* is math
over those verdicts (weighted, capped). An LLM's free-pick number clusters at 72/82 and hides gate
failures; the computed score is differentiated and reproducible, and a genuine critical-gate UNMET
can never come out as 40+. Follow the same split here: you judge the 7 dimensions, `compute_score.py`
produces the number.

## The scoring math (what compute_score.py does)

- Weights: core 24 · seniority 20 · domain 14 · communication 14 · environment 12 · education 8 · trajectory 8
- met = full · partial = half · unmet = 0, normalized to 0-100
- Critical gates = core / seniority / communication; caps at 38 / 24 / 14 for 1 / 2 / 3 UNMETs
- Corrections: `evidence_type:"negative"` forces UNMET; an UNMET with no evidence, or a neutral UNMET
  with no mismatch language, is upgraded to PARTIAL; on thin profiles, unsupported critical-dim UNMETs
  become PARTIAL. (These run inside the script — they may adjust a verdict you passed in.)

## Files
- `RUBRIC.md` — the verbatim 7-dimension instruction text (byte-identical to production). **Read this to score.**
- `scripts/compute_score.py` — no-API scorer: verdicts JSON → the exact number + breakdown.
- `scripts/score.py` — *optional* fully-automated variant that calls the Claude API end-to-end
  (needs `ANTHROPIC_API_KEY`). Not needed for in-conversation scoring; use it only for batch jobs.
- `scripts/build_skill.py` — re-extracts everything from `ranking.py` if the production rubric changes.

## Fidelity
Rubric text and scoring math are byte-identical to `ranking.py` (verified: same mock breakdown →
prod 38, skill 38). The one thing that differs from the app: the derived SCORING FRAME and the
mined company-tech hint aren't DB-backed here — you derive the frame in step 2, and the company-tech
nudge (a soft PARTIAL signal, `""` for most profiles) is skipped. Neither can flip a gate.
