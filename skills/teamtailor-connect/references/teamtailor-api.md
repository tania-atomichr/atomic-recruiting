# Teamtailor API — the working reference

Everything here is verified against the atomic-HR NA instance. `scripts/tt_client.py` implements
the setup + pagination so you rarely hand-roll a request; this file is the map and the *why*.

## Setup
- **Base**: `https://api.na.teamtailor.com` (the NA instance — a US/EU base will 401).
- **Headers**: `Authorization: Token token=<KEY>` and `X-Api-Version: 20240904`. Both required;
  a missing/newer `X-Api-Version` changes payloads or 406s.
- **Format**: JSON:API — `{data, included, links, meta}`. Records are `{id, type, attributes,
  relationships}`. Sideload related records with `include=` and read them from `included`.
- **Key**: `tt_client.resolve_key()` uses env `TEAMTAILOR_API_KEY`, else the `API_KEY = "..."`
  literal in `teamtailor_flag.py` (the daily spam-flag job in `~/Claude zinspector`). That script
  is the one path proven to work from this machine.

## Two rules that bite
- **`page[size]` max is 30.** Larger returns HTTP 400. `get_pages()` forces 30 and follows
  `links.next` to the end.
- **Rate limit ≈ 48 requests / 10s.** The client backs off on 429/5xx. Anything that loops
  per-candidate (enrichment) should keep the working set small and can run in the background.
- **Totals without paging**: `meta.record-count` on the first page of any collection.

## Resource map (what lives where)
| Resource | Key attributes / notes |
|---|---|
| `candidates` | `first-name`,`last-name`,`email`,`phone`,`resume-summary` (HTML), `profile-url`, `tags`. Department is **not** on the candidate — it's a job attribute. |
| `job-applications` | join of candidate↔job; `created-at`, `sourced`. Filter: `filter[job]` (NOT `filter[job-id]`). |
| `jobs` | `title`, `status`; `include=department`. ~40+ jobs. |
| `stages` | pipeline stages; name e.g. "Reviewing". |
| `departments` | Engineering, Ops, etc. `filter[department]` works on candidates. |
| `custom-fields` | field definitions; match by `api-name`. |
| `custom-field-values` | per-candidate values; the value's **owner** is the candidate. |
| `locations` | `city`,`country` — the reliable "based in" signal. |
| `activities` | per-candidate feed (`GET /v1/candidates/{id}/activities`); `code=="share"` etc. |

## Custom fields that matter (recruiter-filled)
`screened` (checkbox), `english-level` (CEFR, e.g. `["Advanced (C1)"]`), `salary-expectations`
(monthly USD), `years-of-experience`, `description`, `startup-experience`, `stability`,
`agency-experience`, `portfolio`. Trust these over application-form self-ratings.

## Query cookbook
`from tt_client import get_pages, get_one`

**Connectivity + record counts** — `python3 tt_client.py` prints totals for the core resources.

**List the open jobs / find a JOB_ID**
```python
jobs, dep = get_pages("jobs", {"include": "department"})
for j in jobs: print(j["id"], j["attributes"]["title"], j["attributes"]["status"])
```

**Applicants for a job (with candidate + stage)**
```python
apps, inc = get_pages("job-applications", {"filter[job]": JOB_ID, "include": "candidate,stage"})
stages = {i["id"]: i["attributes"]["name"] for i in inc if i["type"] == "stages"}
```

**One candidate, fully expanded**
```python
c = get_one(f"candidates/{cid}",
    {"include": "custom-field-values.custom-field,locations,job-applications.job"})
a = c["data"]["attributes"]                     # resume-summary, profile-url, email, tags
```
Map custom fields by joining `custom-field-values` → `custom-fields.api-name` (see enrich.py).

**Every screened candidate across the DB** — see the `screened-candidate-search` skill; the trick
is `GET /v1/custom-field-values?filter[custom-field]=<screened id>&include=owner` and keeping
values whose `value == "true"` (the checkbox is the **string** "true", not a boolean).

## Links & privacy
- `profile-url` (→ `app.na.teamtailor.com/...`) is durable — the single link to a candidate's CV,
  screening notes, and interview scorecards. Use it in any deliverable.
- Raw resume-PDF URLs from the API are **signed and expire in ~60s** — never paste them somewhere
  read later. There is **no** standalone interview-recording/transcript URL in the API.
- Writes (PATCH candidate summary, POST jobs/applications) are possible but out of scope here —
  the `candidate-review-to-client` and `candidate-summary` skills own those.
