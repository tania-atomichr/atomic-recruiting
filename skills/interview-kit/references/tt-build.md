# Part 4 — Building the kit in Teamtailor (internal app API)

Interview kits are NOT on the public TT API. Everything here goes through the internal app API, using the recruiter's logged-in session in Chrome (Chrome MCP `javascript_tool` running `fetch` in a tab on app.teamtailor.com).

## Setup
- Base: `https://tt.na.teamtailor.com/app/companies/{{TT_COMPANY_ID}}/api/`
- Headers on EVERY request or you get 404: `{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','X-Ember-Route':'settings.interview-kits.index'}` plus `credentials:'include'`.
- Long batches: run as a detached async IIFE writing progress to a `window.__state` object (synchronous eval times out at 45s), poll the state object.

## ⚠️ THE LANDMINE — read before any PUT
A PUT of a kit record does a **FULL REPLACE of nested collections**. Anything not in the payload is silently deleted (200, empty arrays). Echoing back the plain `picked_questions` / `scorecard_picks` arrays also wipes them. The only safe write:
- send COMPLETE `picked_questions_attributes` (rows to keep WITH their `id`, new rows without an id),
- send COMPLETE `scorecard_picks_attributes` (same rule),
- set `competence_order` as `[{id:'<questionId>', type:'question'}, …]` for the free-flowing questions,
- `delete kit.picked_questions; delete kit.scorecard_picks;` before PUT,
- GET after and verify counts before declaring success.
This wiped 61 kits once (2026-07-06). Do not improvise here.

## Build sequence

**0. Search the bank BEFORE creating anything (mandatory).** For each authored question, check whether an equivalent already exists:
- Public API: `get_pages("questions")` via the teamtailor-connect client (793+ records with `title`), match on role keywords, tool names, and intent — not just exact titles.
- Internal API: `GET questions?query=<keywords>&per_page=25` (same headers) mirrors the kit editor's search.
Reuse rule: same intent = reuse the existing id, even if the wording differs slightly (if the wording should improve, that's an edit to the existing question, which propagates — not a new question). Only questions with genuinely new intent get created. Record reused-vs-created per question for the Notion page and the final summary.

**1. Create the genuinely new questions** — `POST questions` with
`{question:{type:'Question::Text', title:'…', description:'<full script incl follow-up chain>', scorecard_criterium_id:67334}}` → 201 (verified live 2026-07-07, created #212162).
**Tags write via `tag_list` (names), NOT `tag_ids` (read-only on write, silently ignored).** After the POST, PUT the question with `tag_list:['interview kit','<client>','<role>']` — lowercase client and role tags (minting them is fine for questions per Tania 2026-07-07; reuse exact existing spellings via `GET tags?query=`). **The title stays clean — no role or client suffix in it; that's what the tags are for.** Every question carries BOTH the **skill** (`scorecard_criterium_id`: Core skills 67334 mostly, Domain 67338 for business-model probes) and its tags. When REUSING an untagged bank question, fix its skill + add the `interview kit` tag the same way (safe, verified) — but do NOT retitle or add role/client tags to reused questions that other kits share.

**2. Read the Template live** — `GET interview_kits/{{TT_TEMPLATE_KIT_ID}}` (fallback: find by `interview_kits?template=true…` name "Template"). Its `picked_questions`, `competence_order`, `scorecard_picks` are the skeleton.

**3. Create the kit** — preferred: `POST interview_kits` with `{interview_kit:{name:'{Role} IK | {Client}', template:true, is_hidden:false, is_available_everywhere:true, picked_questions_attributes:[…skeleton rows without ids…, …new role questions…], competence_order:[…], scorecard_picks_attributes:[…from Template, without ids…]}}`.
POST kits → 201, verified live 2026-07-07 (created kit 16753). If a session's permission layer blocks it, fallback: click **"Duplicate interview kit"** on the Template row in the UI, then PUT the duplicate with the safe recipe.

**Kit metadata (always set, verified live):**
- `name`: `{Role} IK | {Client}` — the naming convention, no exceptions.
- `tag_list: ['<client>', '<area>']` — lowercase client name (e.g. `roverpass`) + practice area (`sales`, `marketing`, `engineering & product`, `executive support`, `operations`, `finance & accounting`). Kit tags MAY be minted if missing (Tania's call 2026-07-07) — but reuse exact existing spellings (`GET tags?query=`) so the vocabulary stays clean. The role is NOT a tag; it's already searchable in the kit name.
- `instructions` (HTML): the **session goals** from Part 1 (as a bulleted list, with the seniority-read line), then a **"NUMBERS TO CAPTURE"** line — the 3-5 scale/outcome metrics for this role, derived from the brief's Key Success Indicators and the units-by-function table (e.g. for an SDR: "outreach volume/week · demos booked · response time · accounts juggled"). The recruiter doesn't ask them all; they know which numbers to catch when they fly by — they feed the notes and the client summary. Then links to the **Opportunity Brief** and the **Notion kit page**. This renders for whoever runs the call — it's the interviewer's cheat sheet.
**Layout — how kit order really works (verified live 2026-07-07):** `competence_order` is the FULL layout and accepts two entry types: `{id:'<questionId>',type:'question'}` for untagged questions and `{id:'<criteriumId>',type:'competence',children:[]}` for skill sections. Skill-tagged questions ALWAYS render inside their skill's section wherever that section sits — placing them as question entries does nothing. **Every untagged picked question MUST appear in competence_order or it disappears from the layout (and risks being async-stripped).** The canonical call-order layout:
**The layout recipe lives in `canonical-kit.md` — read it; do NOT improvise section order.** Summary: all questions are skill-tagged, the layout is pure section ordering (competence entries), the Core-skills section (the 🧩 domains) inserts after Attitude and before Education in the Template's LIVE order, and **within-section order is set via the competence entry's `children` array** (row_order is ignored for section members — e.g. Conclusion children must be [Wrap-Up, Final Recommendation]). (`row_order_position`, not raw row_order, for reordering scorecard_picks on updates with ids.)

**Whole-kit coherence pass (mandatory before verifying):** read the assembled kit top to bottom as a script and check every 🧩 domain against the ★ canonicals — one home per signal. Typical dupes to resolve per kit: a role-specific scope domain vs **★ Scope of Work** (keep the domain's craft-scope, the generic ★ stays for the ownership pattern — but if they literally repeat, drop the weaker one FROM THIS KIT only); a business-model domain vs **★ Business & Customers ✳️** (the ✳️ is skippable, so overlap is tolerable — note it in the Notion page); an AI domain vs **★ Curiosity & AI** (KEEP BOTH — Tania's rule, different purposes). Never edit the Template or a ★ canonical in passing; canonical improvements are raised separately.

**4. Verify twice** — GET the new kit: question count, order, scorecard picks all match intent. Then open `https://app.teamtailor.com/companies/{{TT_COMPANY_ID}}@na/settings/interview-kits/<id>/edit` and read the page: every question renders, skill-tagged ones sit under their sections.

**5. Attach to the job** — through the job's **Edit → Evaluation** tab UI (verified flow 2026-07-07): open `/jobs/<id>/edit/evaluation`, click "Select interview kit" (the dropdown opens even from a JS `.click()`; the option list renders after ~1s — scroll down if the control is below the fold and use real computer-clicks for the option), type the kit name in the search, click the kit ("Interview kit added" toast), then click **Save**. Verify server-side: `GET jobs/<id>` → `job_detail_id` → `GET job_details/<did>` shows the kit in `picked_interview_kits` AND `picked_questions` (the application form) still has its rows. Never write the attachment directly against job_details — full-replace risk on the application form.

## Rules
- Archive, never delete. Questions with answers must never be deleted (history references them).
- If anything verifies wrong, STOP and restore from the GET snapshot you took before writing (always snapshot first: `window.__backup = kit` + keep it in the transcript).
- When done, drop the kit URL and the Notion page URL in the final summary.
