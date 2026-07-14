---
name: screened-candidate-search
description: >-
  Source candidates from the whole Teamtailor screened pool and deliver ONE ranked spreadsheet
  mapping people to a set of target roles. Use whenever the user (an atomic-HR recruiter) wants to
  find, source, or shortlist screened candidates for open roles — e.g. "find me screened SDRs and
  account managers for [client]" or "pull LATAM support + onboarding candidates into a sheet". It
  queries the TT API for every screened candidate, drops irrelevant areas (engineering, design,
  marketing), classifies each into the target roles, enriches them (salary, English, country, last
  application, title), ranks them with a one-line why and a 0-10 fit, and writes a single sheet where
  Role is a column (never one tab per role) for Google Drive. On request it can also INJECT the very
  best (quality-gated: fit ≥ 8, no critical gaps, capped ~5, deduped) into a Teamtailor job as
  Sourced candidates for the recruiter to review later — the natural follow-on after tt-post-job
  posts a role. Trigger it even when the user names one
  role or doesn't say "screened". This is the SOURCING counterpart to candidate-review-to-client
  (which packages an already-chosen review stage) — use THIS one for open-ended "who's in the pool"
  searches; lean on teamtailor-connect for raw API basics.
---

# Screened-candidate search → one ranked spreadsheet

The recruiter has ~2,000 screened candidates sitting in Teamtailor and a handful of open roles.
This skill turns that into a single, sortable spreadsheet: every relevant candidate on one row,
tagged with which target roles they fit, ranked, and enriched with the facts she needs to decide
at a glance (salary, English, country, when they last applied, current title).

The deliverable that works is **one sheet with Role as a column** — she does not want a tab per
role, and she wants to filter and edit it in Google Drive. Everything below serves that.

For raw API mechanics (auth, the `page[size]=30` cap, the resource map) this skill relies on the
**teamtailor-connect** skill; the sourcing-specific gotchas are in `references/sourcing-notes.md`.
Read that once before starting.

## The pipeline (scripts do the plumbing, you do the judgment)

Four bundled scripts in `scripts/` handle the deterministic, error-prone parts (auth, pagination,
the screened-pool enumeration, per-candidate enrichment, writing the exact CSV schema). Your job is
the judgment they can't do: translating the user's role descriptions into a keyword config, and
ranking the survivors. Run the scripts from a scratch working dir.

```
harvest_screened.py  →  classify.py  →  enrich.py  →  [you rank]  →  build_sheet.py
   whole pool           drop noise,     structured                    one sheet
   + summaries          bucket to roles fields                        (Role = column)
```

### 0. Confirm the roles and the client's real business
Get the client and a 1-2 line description of each target role. **Identify the client's OWN business
first** (e.g. "a campground / RV-park reservation SaaS"), because "relevant" is judged
against who they are and who they sell to, not against the candidate's past industry. Note any geo
preference — LATAM is usually preferred (cost + same timezone), so surface LATAM candidates first
and flag the handful of US/Canada ones rather than dropping them silently.

### 1. Translate the roles into a config
Copy `assets/roles.example.json` and rewrite it for this search. Each role gets a `keywords` list —
the terms that show up in a screening summary when someone has done that job. Be generous with
synonyms (SDR ≈ BDR ≈ outbound ≈ prospecting); a too-narrow list makes a role's pool come back
tiny. Set `exclude_areas` to the areas clearly off (engineering, design, pure marketing, finance).
Save it as `roles.json` in the working dir.

### 2. Harvest the whole screened pool
```
python3 scripts/harvest_screened.py --out work/screened.jsonl
```
Pulls every screened candidate (~2,000) *with their screening summaries* in one pass. Smoke test
first with `--limit 60` to confirm connectivity cheaply.

### 3. Classify and drop the noise
```
python3 scripts/classify.py --roles roles.json --in work/screened.jsonl --out work/classified.jsonl
```
Keyword-buckets the pool into the target roles and drops irrelevant areas — ~2,000 down to a few
hundred. It prints the per-role counts. **If a role comes back with a suspiciously small pool,
widen that role's keywords and re-run this step** (no need to re-harvest). Keyword-first is
deliberate: the summaries are keyword-dense, and your judgment is better spent ranking the
survivors than triaging 2,000 people one at a time.

### 4. Enrich the survivors
```
python3 scripts/enrich.py --in work/classified.jsonl --out work/enriched.jsonl
```
One detail call per candidate for salary, English-level field, country (from `locations`, not the
phone), years of experience, and last application (date + role). A few hundred candidates take a
couple of minutes; it's safe to run in the background and re-runs resume where they left off. The
`english-level` field is often blank — expected; you'll fill it in the next step.

### 5. Rank them (this is the part only you can do)
Read `work/enriched.jsonl` and write `work/ranking.json` — a list of objects, one per candidate you
want scored, carrying the judgment the scripts can't:

```json
[
  {"id": "4384644", "best_role": "SDR / Outbound", "fit": 9,
   "why": "Heads SDR team, 50-80 daily outbound calls, healthcare SaaS",
   "english": "Advanced (C1)", "title": "Bilingual Sales Professional", "ft_pt": "Full-time"}
]
```

- **`why`** is one tight line — the single reason she'd click this person. It's the column she reads
  first; make each specific (numbers, domain), not "strong CS background".
- **`fit`** is 0-10 against the role's real demands and the client's business. Give hospitality /
  property-ops people a bump for a hospitality-SaaS client — that's on-domain.
- **`english`**: if the structured field was blank, parse the level from the summary prose (every
  summary states it somewhere). Don't leave it empty.
- **`title`**: the candidate's most recent role, read from the top of their summary.
- **`ft_pt`**: only if stated (genuinely sparse in TT); leave blank rather than guessing, so a
  blank honestly means "confirm before submitting".

You don't have to rank every survivor — cover the ones worth surfacing. Anyone you omit still lands
in the sheet via the keyword classification, just with a blank Fit/Why.

### 6. Build the one sheet
```
python3 scripts/build_sheet.py --roles roles.json --in work/enriched.jsonl \
    --ranking work/ranking.json --out <client>_candidates.csv
```
Produces the single CSV, sorted by Best role then Fit. Columns: `Best role, Fit (0-10)`, one ✓
column per target role (the matrix — lets her filter to "anyone who could do Support"), `Why, Name,
Country, Recent title, English, Salary/mo, FT/PT, YoE, Last applied role, Last applied, TT profile,
Email, Screening summary`.

### 7. Deliver to Google Drive
The recruiter wants this as an editable Google Sheet on her Drive.
- If a **write-enabled** Google Drive tool/connector is available, upload the CSV and let Drive
  convert it to a native Sheet (its CSV import does this automatically).
- The Drive connector is often connected **read-only** — if the upload is rejected for permissions,
  don't fight it. Tell her the file is ready locally and that dragging it into drive.google.com
  opens it directly as an editable Sheet. Don't block the whole deliverable on the upload.

### 8. (Optional) Inject the best into the TT job as Sourced — QUALITY-GATED
When the user wants candidates placed on a Teamtailor job for later review (typical right after
tt-post-job creates the role's job), attach them via the public API (live-verified 2026-07-03):

```json
POST /v1/job-applications
{ "data": { "type": "job-applications",
    "attributes": { "sourced": true },
    "relationships": {
      "candidate": { "data": { "type": "candidates", "id": "<id>" } },
      "job":       { "data": { "type": "jobs",       "id": "<jobId>" } } } } }
```

`sourced: true` lands them as **Sourced** in the job's Inbox — visibly added-by-us, waiting for
review. **Quality beats volume here; this is a hand-picked shortlist, not a pipeline dump:**

- **The gate (all must hold):** `fit ≥ 8` from your ranking · no critical-dimension gap against the
  role's brief/OB (core skills, English when client-facing, geo, salary-vs-band when both are
  known) · a specific `why` you'd defend to the recruiter. When in doubt, leave them in the sheet
  instead — the sheet is the wide net, the job is the shortlist.
- **Cap: 5 by default** (the user can raise it). A recruiter reviews a Sourced list of five; a list
  of forty gets ignored.
- **Dedup first:** `GET /v1/job-applications?filter[job]=<jobId>` and skip anyone already on the
  job (re-POSTing creates duplicates).
- **Never advance stages, never message, never reject.** The injection is the entire write; every
  decision after Sourced belongs to the recruiter in TT.
- **Verify + report:** re-GET the job's applications, confirm the count, and report each injected
  candidate as name + fit + the one-line why + TT profile link, so the review can start from the
  summary alone.

## What to get right (and why)

- **Use the TT profile link, never a resume-PDF URL.** The profile link is durable and is the one
  place the CV + screening notes + any interview scorecards live. Raw PDF links from the API are
  signed and die in ~60s — dead by the time she opens the sheet.
- **Country from `locations`, not the phone.** A US phone number on a Mexico-based candidate is
  common; the location record is the truth.
- **Don't fabricate.** Salary, English, FT/PT come from the data or the summary. A blank is more
  useful to her than a guess — she acts on these; an invented "Full-time" wastes a screen.
- **LATAM first.** Sort/flag so preferred-geo candidates are on top; surface off-geo ones as a
  short flagged tail rather than deleting them.

Underlying API mechanics and every gotcha: `references/sourcing-notes.md` and the
**teamtailor-connect** skill's `references/teamtailor-api.md`.
