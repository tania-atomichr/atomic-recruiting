# Teamtailor API patterns

Key resolves from `teamtailor_flag.py` (`API_KEY = ...`) or env `TEAMTAILOR_API_KEY`. Base
`https://api.na.teamtailor.com`. Headers: `Authorization: Token token=<KEY>`, `X-Api-Version: 20240904`.
Max `page[size]` = 30 (larger 400s). JSON:API format. Rate limit ~48/10s; back off on 429.

## 1. Review-stage candidates for a job
```python
import requests
H={"Authorization":f"Token token={KEY}","X-Api-Version":"20240904"}
def pages(url,params):
    params=dict(params); params["page[size]"]=30
    r=requests.get(f"https://api.na.teamtailor.com/v1/{url}",headers=H,params=params,timeout=45).json()
    data=list(r["data"]); inc=list(r.get("included",[]))
    while r.get("links",{}).get("next"):
        r=requests.get(r["links"]["next"],headers=H,timeout=45).json()
        data+=r["data"]; inc+=r.get("included",[])
    return data,inc
apps,inc=pages("job-applications",{"filter[job]":JOB_ID,"include":"candidate,stage"})
stages={i["id"]:i["attributes"]["name"] for i in inc if i["type"]=="stages"}
from collections import defaultdict
bystage=defaultdict(list)
for a in apps:
    st=a["relationships"].get("stage",{}).get("data")
    bystage[stages.get(st["id"]) if st else "?"].append(a["relationships"]["candidate"]["data"]["id"])
# target stage usually "Reviewing"
```
`filter[job]` is the allowed filter (NOT `filter[job-id]`). To find the JOB_ID, list jobs:
`GET /v1/jobs?page[size]=30&include=department` and match the title.

## 2. Candidate detail, trusted fields, summary status
```python
c=requests.get(f".../v1/candidates/{cid}",headers=H,
   params={"include":"custom-field-values.custom-field,locations,job-applications.job"}).json()
a=c["data"]["attributes"]
# a["resume-summary"] (HTML), a["tags"], a["profile-url"], a["email"], a["phone"]
cfmap={i["id"]:i["attributes"]["api-name"] for i in c["included"] if i["type"]=="custom-fields"}
fields={}
for i in c["included"]:
    if i["type"]=="custom-field-values":
        fields[cfmap[i["relationships"]["custom-field"]["data"]["id"]]] = i["attributes"]["value"]
# TRUSTED recruiter-filled fields:
#   fields["english-level"]  -> e.g. ["Advanced (C1)"]  (CEFR; trust this over app-form self-rating)
#   fields["salary-expectations"] -> number
#   fields["years-of-experience"] -> number (often absent; then derive from CV/transcript)
#   fields["screened"] -> "true" (checkbox values are the STRING "true", not boolean)
```
Country: `locations` relationship (city+country) is cleanest; phone prefix is a weak fallback.
Detect "needs summary": `("Tech Stack" in resume-summary and "Core Competencies" in resume-summary)`
means it's already in our format; otherwise it needs one.

## 3. Enumerate ALL screened candidates (if you need the wider pool, not just a stage)
The `screened` checkbox is a candidate custom-field. To list everyone screened:
`GET /v1/custom-field-values?filter[custom-field]=<SCREENED_FIELD_ID>&page[size]=30&include=owner`
(find the field id from `GET /v1/custom-fields`). `include=candidate` is NOT valid; use `include=owner`
— the owner is the candidate. Keep values whose `value=="true"`.

## 4. Write the summary (PATCH)
```python
Hj={**H,"Content-Type":"application/vnd.api+json"}
r=requests.patch(f".../v1/candidates/{cid}",headers=Hj,
   data=json.dumps({"data":{"id":cid,"type":"candidates","attributes":{"resume-summary":HTML}}}))
assert r.status_code==200
assert "—" not in HTML   # em-dash gate
```
The `resume-summary` field IS the Resume→Summary tab in the TT UI and travels in client shares.

## 5. Create draft jobs / attach sourced candidates (only if asked to build internal pools)
Create job: `POST /v1/jobs` with `{"data":{"type":"jobs","attributes":{"title":...,"body":...,
"status":"draft"},"relationships":{"user":{"data":{"type":"users","id":RECRUITER_USER_ID}}}}}`
(user relationship is required). Attach candidate: `POST /v1/job-applications` with
`{"data":{"type":"job-applications","attributes":{"sourced":true},"relationships":{"candidate":
{...},"job":{...}}}}` — `sourced:true` means the candidate is NOT notified.

## 6. Verify a share was sent
After generating a share (browser), confirm via the activity feed:
`GET /v1/candidates/{cid}/activities?page[size]=1&sort=-created-at` → newest activity `code=="share"`
with a recent timestamp. The share `data` holds `{emails, subject, body}` but NOT the share URL/token
(the token only lives in the email — that's why Phase 4/7 read Gmail).
