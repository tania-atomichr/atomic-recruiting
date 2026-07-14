---
name: candidate-review-to-client
description: >-
  End-to-end pipeline for taking screened candidates sitting in a Teamtailor review stage and
  packaging them to send to a client: pull each candidate's interview transcript + CV, write
  client-facing summaries into their TT Resume-Summary field, score and rank them against the
  role with candidate-fit-score, generate client-safe share links, and draft a Slack message to
  the client. Use this whenever the user (an atomic-HR recruiter) wants to share candidates with
  the client or hiring manager, prep the review-stage candidates, write the summaries and send
  them to a client, shortlist for a role, or references a Teamtailor review/Reviewing stage and
  a client contact by name. Trigger it even if
  they only ask for one part (e.g. "write summaries for everyone in review") since it orchestrates
  the whole flow plus the sub-skills candidate-summary and candidate-fit-score. Not for generic
  candidate search/sourcing, only the review-to-client hand-off.
---

# Candidate review → client hand-off

This skill turns a Teamtailor review stage full of screened candidates into a client-ready
package: summaries written into TT, a fit ranking, client-safe share links, and a drafted
client message. It composes two existing skills — **candidate-summary** (writes the summaries)
and **candidate-fit-score** (scores them) — and adds the Teamtailor / Gmail / Slack mechanics.

The whole point is that the recruiter has already screened these people; this skill does the
mechanical, error-prone hand-off work consistently so nothing is fabricated and nothing leaks to
a client that shouldn't.

## The one thing to get right first: CONFIRM THE ROLE

Candidates get staged into a job, but the *role they're being pitched for* is not always the job's
label, and the fit score + client message are only meaningful against the right brief. Before
scoring or drafting anything, **confirm with the user which role/brief these candidates are for**
(and get the JD or a 2-3 line brief). Getting this wrong inverts the entire ranking. If a client
Slack channel exists, the JD is often pasted there — but still confirm, don't assume.

## Setup (read once)

- **TT API**: base `https://api.na.teamtailor.com`, headers `Authorization: Token token=<KEY>` and
  `X-Api-Version: 20240904`. The key lives in `teamtailor_flag.py` in the recruiter's working dir
  (`~/Claude zinspector`). Max `page[size]` is 30. Use Bash + `python3`/`requests` for all API calls.
- **Browser**: uses the claude-in-chrome MCP against the recruiter's logged-in Teamtailor. Drive
  the share dialog with the **javascript_tool**, not coordinate clicks (they're flaky on this SPA).
  Full recipes in `references/share-links-browser.md`.
- **Sub-skills**: invoke `candidate-summary` for the summary format/rules and `candidate-fit-score`
  for scoring. This skill tells you *when* and *with what inputs*.

## Workflow

Work phase by phase. Track progress with a task list — this is long and it's easy to lose a candidate.

### 1. Scope the review stage
Get the job's applications and find the review stage's candidates:
`GET /v1/job-applications?filter[job]=<JOB_ID>&page[size]=30&include=candidate,stage` (paginate).
Group by stage name; the target is usually named **"Reviewing"** (confirm if ambiguous). Collect the
candidate IDs + names. See `references/teamtailor-api.md` for exact snippets.

### 2. Detect who still needs a summary
For each candidate read `resume-summary`. A **proper** summary contains the markers `Tech Stack` /
`Core Competencies` (our format); anything else (a bulleted résumé extract, or short/empty) **needs**
one. Only process the ones that need it — don't overwrite good summaries.

### 3. Screen for data-quality flags (check, don't exclude)
Read each candidate's `tags` and recent comment activities for `spam-likely`, `spam-suspicious`,
`wrong author`, `duplicate`. These are often **automated false positives** — surface them to the
user and confirm, but do NOT drop a candidate just because of an auto-tag. Only genuinely bad data
(a transcript/CV that clearly belongs to a different person) should be skipped, and flagged.

### 4. Get transcripts + CVs
The interview transcript is NOT in the TT public API — it lives on the **public share page**
`https://tt.na.teamtailor.com/shares/<TOKEN>/<CID>`, which contains the transcript **and** the CV
inline (Bash-fetchable, no auth). To obtain the share link:
1. **Generate a share-by-email** to **the current user's OWN inbox** (resolve from
   `ATOMIC_RECRUITER_EMAIL`, else the connected Gmail account, else ask — never a hardcoded person)
   with **Meeting recordings ON** — see `references/share-links-browser.md`.
2. **Retrieve the links from Gmail** — the emails are huge HTML, so **spawn a subagent** to read them
   and return just `{cid: url}` (keeps your context lean). Query: `to:<recruiter> newer_than:1h subject:review`.
3. Fetch each share page and extract transcript + CV text.

(If share links already exist / the user pastes them, skip straight to fetching.)

### 5. Write the summaries
Invoke the **candidate-summary** skill and follow its format exactly. In brief: a flowing,
client-facing note (NO labeled body sections), built from **CV + interview transcript only** (never
the application-form screening answers), with the trusted recruiter custom fields for
`english-level` (CEFR), `salary-expectations`, and `years-of-experience`. NO em dashes. The only
sectioned part is **Tech Stack & Tools** (Core Competencies + Supporting Tools) at the end. PATCH
into `resume-summary` and verify HTTP 200 + readback. For 6+ candidates, fan out to subagents (≈3
each) with the summary spec; have each return a compact record `{cid,name,country,english,salary,
yoe,recent_role,highlight,flag}` so you have the data for later phases without re-reading transcripts.

### 6. Score & rank
Invoke **candidate-fit-score** against the **confirmed** role brief (Phase 0). For many candidates,
have one subagent score them all (consistency) using each candidate's `resume-summary` as the
profile; it returns a ranking with the 7-dim breakdown. The score comes from the skill's
`compute_score.py`, not eyeballing.

### 7. Generate client-safe share links
A second share per candidate, limited to **contact info + résumé + summary only** (Personal
information + Resume + Resume summary; everything else OFF — no recordings, Q&A, internal docs).
Send to the recruiter's inbox, then retrieve links via subagent (as in Phase 4). Exact JS in
`references/share-links-browser.md` — note it must uncheck **synchronously** (async loops freeze the
renderer) and **gate the send** on exactly the 3 intended fields.

### 8. Draft the client message (ALWAYS a draft — never auto-send)
This is client-facing and external, so you **draft it and hand it to the recruiter for review**;
never post it to the client channel yourself. Before writing, **read the client's Slack history to
learn what THAT hiring manager values** (search their messages) and weave it in — e.g. one client
cares about AI-tool fluency, another about a specific stack or "toughness". Then:
- Rank by the fit score; lead with the genuine fits, be honest about weaker ones.
- Per candidate, a short skimmable blurb of what hiring managers scan for: **based (country), YoE,
  salary expectation, English level, one concrete strength**, and the **client-safe link**. Call out
  the values that specific client cares about where a candidate has them.
- State plainly that **all were pre-screened** and that the recruiter **still needs to confirm each
  one's interest in this specific role**.
- End by asking the client's thoughts and proposing the next step (e.g. a first interview with the
  client's hiring lead).
See `references/client-message.md` for the house style and examples.

## Guardrails (why these matter)
- **Confirm the role first.** The fit score and the whole pitch hinge on it; a wrong brief flips the ranking.
- **Never auto-send to a client.** External, irreversible. Draft → recruiter reviews → recruiter sends.
- **Transcript + CV only for summaries.** Application-form self-answers are off-limits; the recruiter
  considers the interview the credible, current source. Trusted recruiter custom fields override them
  for English/salary/YoE.
- **No fabrication.** If a candidate has no interview transcript, don't invent one — flag it (CV-only
  or needs an interview first).
- **Auto-tags are a prompt to check, not a verdict.** Don't silently exclude flagged candidates.
- **No em dashes / no AI-tells** in any client-facing text.

## References
- `references/teamtailor-api.md` — review-stage lookup, custom fields, PATCH summary, send verification.
- `references/share-links-browser.md` — the javascript_tool recipes (share-by-email full + client-safe), Gmail retrieval, gotchas.
- `references/client-message.md` — reading client values from Slack + house style + draft-only rule.
