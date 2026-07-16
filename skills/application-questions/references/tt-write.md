# Writing the question set to Teamtailor (internal app API)

Questions are NOT writable on the public API (`POST /questions` → **403**). Everything here goes through the internal app API using the recruiter's logged-in Chrome session (Chrome MCP `javascript_tool` running `fetch` in a tab on `app.teamtailor.com`; cross-origin fetch to `tt.na` works with `credentials:'include'`).

## Setup
- Base: `https://tt.na.teamtailor.com/app/companies/{{TT_COMPANY_ID}}/api/`
- Headers on every request: `{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','X-Ember-Route':'jobs.job.edit.index'}` + `credentials:'include'`.
- Internal API returns Rails shape `{question:{...}}` / `{job_detail:{...}}`, not JSON:API `{data}`.

## 0. Search the bank BEFORE creating (mandatory)
`GET questions?query=<craft keywords>&per_page=25` mirrors the editor's search. A ⌖ for this exact craft may already exist (there were already 3 salary variants — do not add a 4th of anything). Same intent = reuse the id. Only genuinely-new intent gets a `POST`.

## 1. Create a genuinely-new ⌖ question
`POST questions` with `{question:{type:'Question::Text', title:'<short spoken question>', description:'<optional nudge>', scorecard_criterium_id:67334}}` → 201 (Core skills 67334 for the craft reality-check).
Then tag it: `PUT questions/{id}` with `tag_list:['application','<client>','<role>']` (lowercase; **`tag_list` names, not `tag_ids`** which are read-only on write). Reuse exact existing tag spellings via `GET tags?query=`; don't mint duplicates. The title stays clean — no client/role suffix, that's what tags are for.

## 2. Attach the full set to the job's application form
The application form persists via **`PUT jobs/{id}`** with nested `job_detail.picked_questions_attributes`. **FULL-REPLACE LANDMINE:** the nested collection is fully replaced on every PUT — send the COMPLETE array (all 6 ✪ + the ⌖), or anything omitted is silently dropped. Existing rows carry their real `id`; new rows use a `lid` (a fresh uuid, `crypto.randomUUID()` in the browser).

Each picked_question row:
```
{ id_or_lid, question_id:<bankId>, mandatory:<bool>, is_qualifying:false,
  owner_id:<jobId>, owner_type:'Job', job_id:<jobId>, row_order:<n*100000> }
```
- The 6 ✪ with the flags from `canonical-set.md` (English/location/salary/availability mandatory; interest/show-work optional).
- The ⌖ reality-check(s): `mandatory:true`, `is_qualifying:false` (set `is_qualifying:true` only when it's a genuine hard gate).
- Also note: **body and pitch live on `job_detail`** and are full-replaced too — if this PUT is the same one that carries the JD, include `job_detail.body` and `job_detail.pitch` or they get nulled. If you're only touching questions, still resend the existing picked rows with their ids so nothing else is disturbed.

The read that shows a job's real current picks: `GET job_details/{job_detail_id}` → `picked_questions` (each with `id`, `question_id`, `mandatory`). Do NOT trust `picked_questions?job_id=X` — that filter is ignored and returns a global set.

## RACE LANDMINE — never chain a full-echo PUT off an immediately-post-write read
After any PUT that touches `picked_questions_attributes`, the very next `GET job_details` can return a PARTIAL/stale set while TT finishes processing server-side. If you then echo that read into another full-replace PUT (e.g. a body update), you make the partial set REAL — questions silently vanish (lost 3 canonicals this way, live, 2026-07-14). Rules: (1) after a questions write, WAIT ~2-3s and VERIFY the count before any further job PUT; (2) verify the question count again after EVERY job-level PUT, even ones "only" touching body/title — the echo is a write.

## Ordering gotchas (verified live 2026-07-14)
- New rows' `row_order` values are reassigned by the server; to ORDER the form, do a second PUT where every row carries its real `id` and `row_order_position` (0,1,2…) — RankedModel ignores raw `row_order` on update.
- **Qualifying questions are PINNED FIRST by Teamtailor** regardless of position — expected behavior (knockouts fail fast), don't fight it.
- Drop a row with `{id:<rowId>, _destroy:true}`.

## 3. Verify
`GET job_details/{job_detail_id}` and confirm: count = 6 + your ⌖, the ⌖ present with `mandatory:true`, the canonicals intact with correct flags. Never declare success on the 200 alone.
