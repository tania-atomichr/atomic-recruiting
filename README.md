# atomic-recruiting — the atomic✳HR recruiting plugin

SOP: what this plugin is, how to install it, and how to use every skill. Audience: the whole atomic✳HR team.

**What this is.** A set of Claude skills that runs the operating system around sourcing: setting up a role, posting it to Teamtailor, seeding it with candidates, and packaging candidates for clients. The sourcing webapp (sourcing.hireatomic.com) remains the engine for lists, scoring, campaigns, and sending. These skills handle everything around it.

**How to use any skill:** describe what you want in plain words ("write the OB for the [role] at [client]", "post the [role] to Teamtailor"). The matching skill triggers on its own. You never need to name the skill, though you can (`/opp-brief`, `/atomic-jd`, and so on).

**The one rule that governs everything:** Claude prepares, you decide. Jobs land as drafts, never published. Candidates land as Sourced, never advanced or messaged. Missing facts get asked, never invented.

---

## Installation

Two steps: install the plugin, then say "set me up" and let the onboarding skill do the rest.

### Step 1 — install the plugin (Cowork)
In Claude (Cowork): **Customize → Plugins → Add new → From marketplace → From repository**, then enter:
```
tania-atomichr/atomic-recruiting
```
(You need access to that private repo first — ask Tania for a GitHub invite.) This supersedes the older `atomic-hr-teamtailor` plugin; if you have that one, remove it so skills are not duplicated.

### Step 2 — say "set me up"
Start a chat and type **"set me up for the recruiting plugin"**. The **atomic-onboarding** skill runs a connection check and walks you through anything missing:

- **Teamtailor API key** — it will ask you for the key (get it from Tania via a password manager, never Slack/email in plain text) and save it to your personal config. Every skill reads it automatically.
- **Your own recruiter email** — the inbox candidate shares go to (yours, not Tania's).
- **Notion** connected to the atomic✳HR workspace.
- **Gmail** on your own recruiting inbox.
- **Chrome** with the Claude extension, logged into Teamtailor.

It ends with a short tour of what you can do. When it shows all ✅, you're ready. Quick self-test: ask "how many open jobs do we have in Teamtailor?"

**Updating later:** in Cowork, Plugins → update `atomic-recruiting` (pulls the latest from the repo), then start a new session.

*Connectors (Notion, Gmail) are authorized in claude.ai connector settings or with `/mcp` in an interactive session — the onboarding skill points you to the right place if one is missing.*

---

## Org config — why the docs say `{{TOKENS}}`

This repo contains **no client names, no staff names, and no org identifiers**: skills reference those as `{{TOKENS}}` (like `{{TT_COMPANY_ID}}`), resolved at runtime from a local file the onboarding skill writes for you (`~/.claude/atomic-recruiting-org.md`). atomic✳HR teammates get the real values automatically from an internal Notion page during "set me up". Anyone else can point the framework at their own Teamtailor + Notion by filling `ORG.example.md`. Numeric record ids that appear in the reference docs (question ids, stage names) are instance-specific too — treat them as the pattern, not literal values.

---

## The golden path: a new role, end to end

```
1. opp-brief             intake call → Opportunity Brief on the role's Notion page
2. atomic-jd             OB → public, client-anonymous JD
3. interview-kit         OB → interview kit in Notion + Teamtailor
4. application-questions 6 standard questions + 2 role reality-checks
5. tt-post-job           everything → fully configured DRAFT job in TT
6. screened-candidate-search   (optional) seed the job with ~5 vetted Sourced candidates
7. YOU review the draft and publish; review the Sourced list in TT
```

Steps 2, 3, and 4 all read from the OB. That is the point of step 1: **the OB is the single source of truth.** Fix facts there, not downstream.

---

## The skills, one by one

### 0. atomic-onboarding — setup + tour
Checks your connections (API key, recruiter email, Notion, Gmail, Chrome), helps you fix anything missing, and shows you what the plugin can do. **Say:** "set me up" or "what can this do?"

### 1. opp-brief — the Opportunity Brief
- **What it does:** turns intake notes, a call transcript, or a rough description into the 8-section house OB (Overview, About Company, About the Role, Ideal Background, Team & Pace, Interview Process, FAQs, Further Reading), and creates it **inside the role's page** in the Open Roles DB.
- **Say:** "write the OB for [role] at [client], here are my intake notes…"
- **It will ask you** for anything critical it doesn't have: comp range, manager, hours, employment type, interview steps. It never invents these.
- **Know:** the OB names the client and quotes comp hourly (the 💡 Atomic market insight callout). Key Success Indicators matter most; the interview kit and screening questions are derived from them.

### 2. atomic-jd — the public job description
- **What it does:** OB → client-anonymous JD in the house voice, plus a structured block the poster consumes.
- **Say:** "draft the JD for [role]" or point it at the role's Notion page.
- **Know:** never names the client ("Our client is a…"), keeps the true metrics (users, years, volumes) for credibility, quotes comp as a **monthly** USD market estimate plus an invitation to share a range. Punchy and specific, no hype words, no em dashes, no About-Atomic footer (the career site adds it). Pitch must fit 200 characters.

### 3. interview-kit — the interview kit
- **What it does:** authors only the role-specific Core Skills questions (canonical ★ questions are reused by id, never rewritten), publishes the kit page inside the role's Notion page, and builds the kit in Teamtailor from the Template.
- **Say:** "build the interview kit for [role]".
- **Know:** kit naming is `{Role} IK | {Client}`. The kit instructions carry the session goals and the NUMBERS TO CAPTURE from the OB's success indicators.

### 4. application-questions — the apply-form questions
- **What it does:** attaches the 6 canonical ✪ questions (location, English, salary, availability mandatory; interest, show-your-work optional) and authors **2 role-specific ⌖ reality-checks**.
- **Say:** "set up the application questions for [role]".
- **Know the ⌖ standard:** each is one open-text question whose answer is a **checkable noun or number** a real practitioner retrieves in two seconds and a bot can't produce ("What ticketing system were you last in, and roughly what daily volume?"). Never a story prompt, never options embedded in the question, never anything the canonicals or the résumé already cover, and always answerable by every legitimate background for the role, including career-changers from the client's own industry.

### 5. tt-post-job — the poster
- **What it does:** builds the complete Teamtailor job: creates it, installs the Atomic 13-stage pipeline with its 6 automations (invite message, smart-schedule under the role's recruiter, confirmation with the OB link, thank-you, survey, submit-todo), sets the Client field, questions, interview kit, and ~14 tailored location cities (a few hubs plus overlooked cities, different per role so posts don't compete with each other).
- **Say:** "post [role] to Teamtailor".
- **Know:** the job lands as a **draft**. Publishing is always a human click. The recruiter on the job is a candidate-experience specialist (fetched live from TT; it asks you which), never the AM.

### 5b. tt-location-rotation — keep postings fresh on the boards
- **What it does:** every ~10 days, swaps the rotating cities on all OPEN jobs (hubs stay) so boards re-syndicate the posting. Deterministic per 10-day window, so re-runs are harmless; changes nothing but locations and verifies that after every write.
- **Say:** "rotate the job locations" — or put it on a schedule (ask Claude to schedule "run tt-location-rotation" every 10 days).

### 6. screened-candidate-search — sourcing from the screened pool
- **What it does:** searches all ~2,000 screened candidates in TT, classifies them into your target roles, enriches (salary, English, country, last application), ranks with a 0-10 fit and a one-line why, and delivers **one spreadsheet** (Role is a column). On request it also **injects the very best into the TT job as Sourced** candidates for you to review.
- **Say:** "find screened candidates for [roles] at [client]" · then "add the top ones to the job".
- **Know the quality gate:** only candidates with fit ≥ 8, no critical gaps, and a defensible why get injected, capped at 5 by default. Everyone else stays in the sheet. Nothing is ever advanced, messaged, or rejected automatically.

### 7. Client-side skills (after screening)
- **candidate-fit-score** — scores a candidate against the brief on the 7-dimension rubric (0-100, MET/PARTIAL/UNMET).
- **candidate-summary** — interview transcript + CV → client-facing summary written into the TT Resume Summary field.
- **candidate-review-to-client** — the hand-off: everyone in the review stage gets summaries, scores, share links, and a drafted client message. Say: "prep the review candidates for [client]".

### 7b. recruiter-email-reply — draft email replies
Paste an email you received (from a candidate, hiring manager, or client) and it drafts a warm, natural, low-friction reply in a recruiter's voice. **Say:** "help me reply to this" and paste the email.

*(The atomic✳HR brand design system lives in the separate private repo `atomic-hr-private`, not here.)*

### 8. teamtailor-connect — the foundation
Direct Teamtailor questions and lookups ("how many candidates do we have?", "list the open jobs"). Every other skill uses it under the hood.

---

## Guardrails (why you can trust it)

| The skills never… | They always… |
|---|---|
| Publish a job | Leave drafts for your review |
| Message, advance, or reject a candidate | Land candidates as Sourced only |
| Invent comp, managers, metrics, or interview steps | Ask you, once, batched |
| Name the client in public copy | Anonymize in the JD, name in the OB |
| Rewrite canonical questions (★ or ✪) | Reuse them by id |
| Delete anything in TT | Archive, or leave it to you |

## Appendix: adding the API key via the terminal (alternative to the chat method)
If you'd rather not paste the key into chat, add it to your shell profile once:
```bash
open -e ~/.zshrc                                    # opens your profile in TextEdit
# add this line at the bottom, with the real key between the quotes:
export TEAMTAILOR_API_KEY="paste-the-key-here"
# save, close TextEdit, then in Terminal:
source ~/.zshrc
echo $TEAMTAILOR_API_KEY                            # should print the key
```
Then start a new Claude Code session. Never commit the key or send it in plain text.

## Known gaps (honest list, as of 2026-07-14)
- ~~tt-location-rotation~~: BUILT (v1.4.0) — see skill 5b above.
- **close** (offer letter + per-client fee/invoice) and **pipeline-report** (weekly funnel): not built.
- Home: https://github.com/tania-atomichr/atomic-recruiting (private). The editable source of truth for the skills lives on Tania's machine in `~/.claude/skills/`; changes are synced here with a version bump.
