# Screened-pool sourcing — notes specific to this pipeline

The API basics (auth, base URL, the `page[size]=30` cap, rate limits, the resource map, the
durable-vs-ephemeral link rule) live in the **teamtailor-connect** skill's
`references/teamtailor-api.md`. Read that first if anything about the raw API looks off. This file
covers only what's specific to sourcing the screened pool into a spreadsheet.

## Enumerating the whole screened population
`screened` is a candidate **checkbox custom-field**, not a stage or tag. To list everyone screened
across all jobs:

```
GET /v1/custom-field-values?filter[custom-field]=<SCREENED_FIELD_ID>&page[size]=30&include=owner
```

- Find `<SCREENED_FIELD_ID>` from `GET /v1/custom-fields` (match `api-name == "screened"`).
  `harvest_screened.py` does this automatically.
- **`include=candidate` is not valid here and 400s.** Use `include=owner` — a value's owner IS the
  candidate, and the included candidate record already carries `resume-summary`, so this single
  pass returns the entire pool WITH the screening write-ups.
- The checkbox value is the **string `"true"`**, never a boolean. Filtering on `== True` silently
  drops everyone (this exact bug ate a whole first run). Compare to `"true"`.

There are ~2,000 screened candidates — which is why we classify and drop before enriching.

## Field meanings for the sheet
- `english-level` (custom-field): recruiter-filled CEFR, e.g. `["Advanced (C1)"]`. **Often blank** —
  when it is, the level is stated in the summary prose ("fluent", "C1", "conversational"). Parse it
  from there in the ranking step; don't leave the column empty when the signal exists.
- `salary-expectations`: monthly USD contractor rate.
- `years-of-experience`: frequently absent → derive from the summary.
- **Country** from the `locations` relationship, not the phone prefix (a US SIM on a LATAM resident
  is common).
- **Last application**: max `created-at` across `job-applications`, with that job's `title`.

## Classification is keyword-first, judgment-second
`classify.py` buckets by keyword because an LLM pass over 2,000 people is wasteful and the
summaries are keyword-dense. It keeps anyone matching *any* target role and only drops on
`exclude_areas` when the role match was a single weak keyword. Spend model judgment on *ranking the
few hundred survivors*, not bulk triage. If a role's pool comes back tiny, widen that role's
`keywords` in the config and re-run `classify.py` — no need to re-harvest.

## The deliverable shape that works
One sheet, **Role is a column** (the recruiter does not want a tab per role). Every surfaced row
gets a one-line `Why` and a 0-10 `Fit`; a ✓-matrix of the target roles lets her filter to "anyone
who could do Support" independent of their Best role. LATAM candidates first, off-geo ones flagged
as a short tail rather than dropped. Columns and sorting are produced by `build_sheet.py`.

## Google Drive delivery
She wants an editable Google Sheet on her Drive. If a **write-enabled** Drive connector is
available, upload the CSV — Drive auto-converts CSV to a native Sheet on import. The connector is
frequently connected **read-only**; if the upload is rejected for permissions, don't fight it —
the CSV is ready locally and dragging it into drive.google.com opens it directly as an editable
Sheet. Don't block the deliverable on the upload.
