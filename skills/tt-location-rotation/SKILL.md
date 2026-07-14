---
name: tt-location-rotation
description: Rotate the location cities on OPEN Teamtailor jobs (~every 10 days) so postings re-syndicate on job boards and stay fresh. Keeps each job's hub cities, swaps the rotating cast of smaller cities for a new deterministic sample, and writes the change with the safe full-echo PUT. Use when the user asks to rotate locations, refresh job postings / re-syndicate on boards, or when a scheduled rotation run fires. One invocation = one rotation pass over all open jobs (or the jobs the user names).
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"; external users: see ORG.example.md in the repo). Read that file once at the start and substitute values before using any URL or id. If it's missing, run onboarding first.

# tt-location-rotation — refresh open jobs' cities so boards re-syndicate

Job boards syndicate postings by city, and a changed `location_ids` set makes boards treat the job as fresh. This skill swaps each open job's **rotating cities** while keeping its **hubs**, roughly every 10 days. Small overlooked cities make a post a standout instead of one of 200; rotating them also reaches new local audiences each cycle.

**Why no stored state:** everything needed lives in TT. The job's current cities are read live, and the rotation seed is derived from the date, so the run is deterministic inside a window and changes across windows. Running twice in the same window is a harmless no-op (same sample), so double-fires are safe.

## The pass, step by step

1. **Resolve tokens + list open jobs.** Internal API base `https://tt.na.teamtailor.com/app/companies/{{TT_COMPANY_ID}}/api/` from the logged-in Chrome tab (same headers as everywhere: `X-Requested-With`, `X-Ember-Route`, `credentials:'include'`). `GET jobs?filter[status]=open&per_page=100` — **only real open jobs**: skip drafts, templates (`template:true`), unlisted, and anything the user excluded. If the user named specific jobs, rotate only those.

2. **Read the pool once.** `GET locations?page[size]=300` (plain `per_page` caps at 50). Group by `region_id`.

3. **Per job — compute the new set** (algorithm + HUB_NAMES list live in `../tt-post-job/references/location-selection.md`, shared so poster and rotator never drift):
   - Read the job's current `location_ids`; infer its region(s) from those cities' `region_id`s. A job with no current locations: skip and report (nothing to rotate).
   - **Keep the hubs**: current cities whose name is in HUB_NAMES stay untouched.
   - **Resample the rest**: run the seeded selection over the region pool minus hubs, with seed = `mulberry32(jobId + windowIndex)` where `windowIndex = floor(days_since_2026_01_01 / 10)` — pass the current date in (no `Date.now()` inside Workflow scripts). Same window → same set (idempotent); next window → new cast.
   - Target total = the job's current count (default 14 if it had the old 79-city dump — this rotation is also the migration that shrinks legacy jobs to the strategic set; flag those in the report).
   - **Skip if unchanged** (same window re-run): don't PUT a no-op.

4. **Write with the SAFE PUT — the full-echo landmine applies.** A bare `PUT jobs/{id} {job:{location_ids}}` → 422 "Client can't be blank", and a careless nested write nulls body/pitch. Echo the live state back: `GET job_details/{id}` first, then PUT with `location_ids` + `job_detail:{ body, pitch, picked_custom_fields_attributes (client row WITH id), picked_questions_attributes (all rows WITH ids), picked_interview_kits_attributes (WITH ids) }`. Exact recipe in `../tt-post-job/references/location-selection.md`.

5. **Verify per job.** GET back: location count correct, body/pitch lengths unchanged, question count unchanged, client intact. Any mismatch → STOP the pass, report the job, do not continue blind.

6. **Report.** One line per job: `title — kept N hubs, swapped M cities (X → Y countries)`, plus skipped jobs and why. Offer (don't auto-write) a light log entry to Notion if the user wants a paper trail.

## Guardrails
- **Open jobs only.** Never touch drafts, templates, archived, or unlisted jobs.
- **Locations are the ONLY thing this skill changes.** The echo-PUT must leave body, pitch, questions, kit, client, recruiter, stages, and triggers byte-identical — that's what the verify step checks.
- **Published jobs are live**: a bad write is candidate-visible. If any verify fails, stop the whole pass and show the user.
- Idempotent by design: re-running inside the same 10-day window changes nothing.

## Scheduling the ~10-day cadence
The skill does ONE pass per invocation; the cadence comes from a schedule. Set it up with the user's scheduling surface (e.g. a scheduled task / routine that prompts: "run tt-location-rotation"). Every ~10 days is the house default (boards re-syndicate on change; more often looks spammy, less often goes stale). The run needs a logged-in TT Chrome session, so schedule it at a time the user's machine is typically active, and have the run report failures loudly rather than retrying silently.
