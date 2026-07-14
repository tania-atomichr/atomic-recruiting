---
name: candidate-summary
description: Generate client-facing candidate summaries from a Teamtailor interview transcript + CV and write them into the candidate's Resume → Summary field via the TT API. Use when the user shares Teamtailor candidate share links (tt.na.teamtailor.com/shares/...) or candidate IDs and asks to write, generate, or enrich candidate summaries.
---

# Candidate Summary (Teamtailor)

Writes a polished, **client-facing** candidate summary into a Teamtailor candidate's
Resume → Summary field, built strictly from the **interview transcript + CV** plus the
**recruiter-filled trusted fields**. The summary is what the client reads to decide on
an interview, so it must read like a sharp recruiter note, not internal notes.

## Inputs
One or more Teamtailor **share links** (e.g. `https://tt.na.teamtailor.com/shares/<token>/<candidateId>`)
or candidate IDs. The candidate id is the trailing number in a share link. An internal
`app.teamtailor.com/.../candidates/<id>` URL also works — treat the trailing number as the candidate id.

## Getting the transcript when you only have a candidate id / internal URL

The transcript can ONLY be read from a **public share page** (`tt.na.teamtailor.com/shares/...`). It is
NOT on the API and NOT reachable from an internal `app.teamtailor.com` candidate URL, so `extract` on a
bare id returns `has_transcript=false` (it still returns CV + trusted fields). Share links can't be
minted via the API either — they're a UI action. So when you don't already have a share link, **generate
one by sharing the candidate to Tania's own inbox, then read the link back from Gmail**:

1. Find the candidate's **job id**: `GET /v1/candidates/<id>/job-applications?include=job`.
2. Open the share modal and send a **full** share (all sections, incl. meeting recordings so the
   transcript travels) to **your OWN inbox** (resolve from `ATOMIC_RECRUITER_EMAIL`, else the connected
   Gmail account, else ask — never a hardcoded person), driving your logged-in Teamtailor via the
   **claude-in-chrome** MCP. Use **Recipe A** in
   `../candidate-review-to-client/references/share-links-browser.md` (navigate to the `modal=share-link`
   URL for that job+candidate, then one `javascript_tool` call). Expect `DONE ... SENT`.
3. Read the link from Gmail: `search_threads` `to:<your-own-inbox> newer_than:1h subject:review`
   (or the candidate name), `get_thread` FULL_CONTENT, pull the
   `https://tt.na.teamtailor.com/shares/<TOKEN>/<id>` line from `plaintextBody`.
4. Run `extract` on that share URL. Now `has_transcript=true`.

Note a candidate can have **multiple interviews** (e.g. an initial screen + a role-fit call), each a
separate transcript. Screening notes may live in a **Notion meeting note** while the role-fit call is the
**TT share transcript** — read BOTH when the user references two interviews, and synthesize across them.

## Workflow (per candidate)

1. **Extract** the inputs (`scripts/tt_summary.py` lives under THIS skill's base directory — use the base path from the skill invocation, wherever the skill is installed):
   ```
   python3 <skill-base>/scripts/tt_summary.py extract "<share_url>" --out /tmp/bundle.json
   ```
   Returns a JSON bundle: `transcript` (verbatim call), `cv_text`, and the **trusted** fields
   `english_level` (CEFR, e.g. "Advanced (C1)"), `years_of_experience`, `salary_expectation`,
   plus `has_transcript`.
   - If `has_transcript` is false, **do not write a summary** — flag it ⚠ (no interview yet;
     the CV alone is not enough for this document).

2. **Read** `transcript` + `cv_text` in full and **write the summary** following the FORMAT
   and STYLE rules below. Save it as HTML to a file (e.g. `/tmp/summary.html`).

3. **Write** it to the candidate's summary field:
   ```
   python3 <skill-base>/scripts/tt_summary.py write <candidateId> /tmp/summary.html
   ```
   (The script refuses to write if an em dash is present.)

4. For a batch, loop steps 1–3 and report a per-candidate log: `✅ <name>` or `⚠ <name> (no transcript)`.
   Show the first 2–3 to the user for sign-off before writing the rest, unless they say do all.

## FORMAT (exact)

A **flowing professional business note** with **NO labeled sections in the body** (no
"Profile Overview", no "Key Strengths"). It flows from a short overview into specifics.
The **only** sectioned part is the **Tech Stack at the very end**.

Weave in, **only if the transcript/CV states it** (never invent):
- Total **years** of experience + industry focus (use trusted `years_of_experience` when present).
- **Languages**: state English at the **CEFR level from the trusted `english_level` field** as a plain
  profile fact (e.g. "English at an Advanced (C1) level"). Never infer level from the call or the
  application-form self-rating. Do NOT write process notes like "the interview was in English".
- **Most recent / most relevant role**: company, industry, title, duration, with **company context**
  (product/SaaS/BPO/agency, size, stage, local vs global) where stated.
- **Scope**: end-to-end ownership vs support, IC vs leadership, with concrete examples.
- **Academic background** if on the CV.
- **Motivation with a sharp, grounded "why now"** (stability, growth ceiling, layoff, role fit) — the
  candidate's real stated reason, no clichés.
- **Availability**: state it cleanly (e.g. "available to start immediately"). Do NOT include
  unflattering or misleading framing (gaps, side gigs like "teaching basketball part-time").
- **Salary**: use trusted `salary_expectation` (matches what they said on the call).

End with:

**Tech Stack & Tools**
**Core Competencies** — bulleted functional groupings adapted to the role (sales: Outbound & Cold
Calling, Full-Cycle Sales, Research & Targeting, Pipeline & Organization; eng: Backend & Infra, AI &
Data, Frontend, DevOps, Mobile; support/CS: Support & Troubleshooting, Tools, Process, etc.).
**Supporting Tools** — actual software/CRM/channels, then Languages. Only tools explicitly mentioned.

## STYLE (hard rules)
- **No em dashes (—) anywhere.** Use commas, periods, colons.
- **No AI tells**: no rule-of-three, no "not just X but Y", no buzzwords (leverage, robust, seamless,
  delve, testament), no emoji, no robotic phrasing. Natural, plain business English.
- **Bold sparingly**, only on scannable facts: years, company names, hard numbers (call volume,
  revenue), CEFR level, salary. Nothing decorative.
- **Client-facing**: it's the candidate's profile, not recruiter notes. No "why I'm telling you this",
  no process/meta, no internal assessment section.
- **Only if stated**: no invented age, fluency level, years, tools, or metrics.
- Concrete numbers, logical flow, crisp, no fluff.

## HTML
Write the field as HTML: `<p>...</p>` paragraphs for the body, `<p><strong>Tech Stack &amp; Tools</strong></p>`,
`<p><strong>Core Competencies</strong></p>` + `<ul><li>...</li></ul>`, same for Supporting Tools.
Use `<strong>` for bold. No `<h1>`/headings needed.

## Notes
- API key: the script reads env `TEAMTAILOR_API_KEY` (the portable path — every teammate sets this),
  else `teamtailor_flag.py` at the repo root (Tania's machine only), else `--key`.
- The transcript is public (share page) and read without auth; the trusted fields and the write use the API.
- A worked reference example lives in the user's memory file `candidate-summary-prompt.md`.
