"""Enrich the classified pool with the structured fields the recruiter cares about.

One detail call per candidate pulls everything in a single include:
    GET /v1/candidates/{id}?include=custom-field-values.custom-field,locations,job-applications.job

From it we read:
  - english-level         (recruiter-filled CEFR field; TRUST over app-form self-ratings.
                           Often BLANK — when so, the level is stated in the summary prose,
                           so leave it empty here and let the ranking step parse it.)
  - salary-expectations   (monthly USD contractor rate)
  - years-of-experience   (often absent -> derive from CV/summary later)
  - country / city        (from `locations` — the reliable "based in" signal; a phone prefix
                           can lie, e.g. a US number on someone living in Mexico)
  - last application      (most recent job-application by created-at, with the job's title —
                           answers "when did they last apply, and for what")

Output: work/enriched.jsonl (classified records + the fields above).

Usage:
    python3 enrich.py --in work/classified.jsonl --out work/enriched.jsonl
Rate limit is ~48/10s; the client backs off on 429, but this still makes one call per
candidate, so a few hundred candidates take a couple of minutes. Safe to run in the
background and re-run — it resumes by skipping ids already in --out.
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tt_client import get_one


def detail(cid):
    r = get_one(f"candidates/{cid}", {
        "include": "custom-field-values.custom-field,locations,job-applications.job"
    })
    inc = r.get("included", [])
    cfname = {i["id"]: i["attributes"].get("api-name") for i in inc if i["type"] == "custom-fields"}
    fields = {}
    for i in inc:
        if i["type"] == "custom-field-values":
            key = cfname.get(i["relationships"]["custom-field"]["data"]["id"])
            if key:
                fields[key] = i["attributes"].get("value")

    # country/city from locations
    country = city = ""
    for i in inc:
        if i["type"] == "locations":
            a = i["attributes"]
            country = a.get("country") or country
            city = a.get("city") or city
            if country:
                break

    # most recent application + its job title
    jobs = {i["id"]: i["attributes"].get("title", "") for i in inc if i["type"] == "jobs"}
    last_date = last_role = ""
    for i in inc:
        if i["type"] == "job-applications":
            created = i["attributes"].get("created-at", "")
            if created > last_date:
                last_date = created
                jr = i["relationships"].get("job", {}).get("data")
                last_role = jobs.get(jr["id"], "") if jr else ""

    def one(v):
        return v[0] if isinstance(v, list) and v else (v if not isinstance(v, list) else "")

    return {
        "english_field": one(fields.get("english-level")),
        "salary": one(fields.get("salary-expectations")),
        "yoe": one(fields.get("years-of-experience")),
        "country": country,
        "city": city,
        "last_applied_date": (last_date or "")[:10],
        "last_applied_role": last_role,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="work/classified.jsonl")
    ap.add_argument("--out", default="work/enriched.jsonl")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.open():
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass

    records = [json.loads(l) for l in pathlib.Path(args.inp).open()]
    todo = [r for r in records if r["id"] not in done]
    print(f"enriching {len(todo)} (skip {len(done)} already done)", file=sys.stderr)

    with out.open("a") as fh:
        for n, c in enumerate(todo, 1):
            try:
                c.update(detail(c["id"]))
            except Exception as e:
                c["_enrich_error"] = str(e)
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
            fh.flush()
            if n % 25 == 0:
                print(f"  {n}/{len(todo)}", file=sys.stderr)
    print(f"enriched -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
