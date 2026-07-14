---
name: teamtailor-connect
description: >-
  Connect to and query the atomic-HR Teamtailor recruiting database through its REST API. Use
  whenever the user (an atomic-HR recruiter) wants to check, query, inspect, count, or pull live
  data from Teamtailor — e.g. "can you check the Teamtailor database with the API?", "how many
  candidates and applications do we have?", "list the open jobs", "look up this candidate", "what
  stages does job X have?", or "give me a pipeline breakdown by stage". It handles auth (key from
  teamtailor_flag.py or TEAMTAILOR_API_KEY), the NA instance and API version, the page[size]=30 cap,
  and rate limits via a bundled Python client, and documents the JSON:API quirks (like the screened
  checkbox being the string "true") so queries don't silently return nothing. This is the foundation
  the other Teamtailor skills build on — reach for it for any direct Teamtailor data lookup. For the
  end-to-end workflow of sourcing screened candidates into a ranked spreadsheet, use
  screened-candidate-search instead.
---

# Teamtailor connect & query

The reliable way to read live data out of the atomic-HR Teamtailor instance. It exists so that
"can you check the Teamtailor DB?" just works — auth, the right base URL and API version, paging,
and the JSON:API gotchas are all handled, instead of being rediscovered every time.

## Start here
1. **Read `references/teamtailor-api.md` once.** It's the resource map + query cookbook + the two
   rules that bite (the `page[size]=30` cap and the `"true"`-string checkbox). Most questions are a
   two-line lookup once you know where a field lives.
2. **Use the bundled client** for all calls — `scripts/tt_client.py` resolves the key, sets the
   headers, paginates, and backs off on rate limits:
   ```bash
   python3 scripts/tt_client.py        # smoke test: prints record counts for the core resources
   ```
   From your own snippet: `from tt_client import get_pages, get_one` (add the script's dir to
   `sys.path`, as the pipeline scripts do). Prefer this over hand-rolled `requests` so you don't
   reintroduce the version/paging/backoff bugs.

## Answering common questions
- **"Is it connected / how big is it?"** → run the smoke test; report the `meta.record-count`
  totals for candidates, job-applications, jobs, stages, departments, users.
- **"List the open jobs" / find a job id** → `get_pages("jobs", {"include":"department"})`.
- **"Who's applied to job X, by stage?"** → `get_pages("job-applications",
  {"filter[job]": JOB_ID, "include":"candidate,stage"})`, then group by stage name.
- **"Look up this person"** → find the candidate id, then `get_one("candidates/{id}",
  {"include":"custom-field-values.custom-field,locations,job-applications.job"})`; report the
  trusted custom fields (English, salary, YoE), country from `locations`, and their applications.
- **"Pipeline breakdown"** → paginate a job's applications and count per stage.

## Principles
- **Report faithfully.** If a call returns 0 or errors, say so and show what you queried — a silent
  empty result is usually the `page[size]` cap or the `"true"`-string filter, not "no data".
- **Never export ephemeral links.** Put the durable `profile-url` in anything the user keeps; raw
  resume-PDF URLs die in ~60s (see the reference).
- **Read-only by default.** This skill reads. Writing summaries or creating jobs/applications
  belongs to `candidate-summary` and `candidate-review-to-client` — hand off rather than PATCH here
  unless the user explicitly asks this skill to write.
- **Don't fabricate.** Numbers and fields come from the API; if something isn't there, say it's not
  populated rather than guessing.
