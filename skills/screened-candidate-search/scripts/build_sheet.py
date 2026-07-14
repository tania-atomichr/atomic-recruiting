"""Build the single deliverable spreadsheet from enriched candidates (+ optional model ranking).

The output is ONE sheet (the recruiter explicitly does not want one tab per role — Role is a
column so she can sort/filter in place). Column order matches what worked in practice:

  Best role, Fit (0-10), <one column per target role>, Why, Name, Country, Recent title,
  English, Salary/mo, FT/PT, YoE, Last applied role, Last applied, TT profile, Email,
  Screening summary

The per-role columns form a matrix: a "✓" means the candidate matched that role's keywords,
so a reader can filter to "everyone who could fit Support" even when their Best role is AM.

Two inputs:
  --in       work/enriched.jsonl (from enrich.py)
  --ranking  optional work/ranking.json authored by the model: a list of
             {"id": "...", "best_role": "...", "fit": 8, "why": "one line", "english": "Advanced (C1)"}
             Provide it to get real Fit + Why per row (the winning deliverable had these on
             every row). Anything you omit falls back to the keyword classification / the
             structured field, so a ranking that only covers your shortlist still builds a
             complete sheet — the rest just have blank Fit/Why.

TT profile is the durable link (put it in the sheet). Do NOT export raw resume-PDF URLs: they
are signed links that expire in ~60s and will be dead by the time she opens the sheet.

Usage:
    python3 build_sheet.py --roles roles.json --in work/enriched.jsonl \
        --ranking work/ranking.json --out candidates.csv
"""
import argparse
import csv
import json
import pathlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", required=True)
    ap.add_argument("--in", dest="inp", default="work/enriched.jsonl")
    ap.add_argument("--ranking", default="")
    ap.add_argument("--out", default="candidates.csv")
    args = ap.parse_args()

    cfg = json.loads(pathlib.Path(args.roles).read_text())
    role_names = [r["name"] for r in cfg["roles"]]

    rank = {}
    if args.ranking and pathlib.Path(args.ranking).exists():
        for row in json.loads(pathlib.Path(args.ranking).read_text()):
            rank[row["id"]] = row

    records = [json.loads(l) for l in pathlib.Path(args.inp).open()]

    header = (["Best role", "Fit (0-10)"] + role_names +
              ["Why", "Name", "Country", "Recent title", "English", "Salary/mo",
               "FT/PT", "YoE", "Last applied role", "Last applied", "TT profile",
               "Email", "Screening summary"])

    def salary_fmt(v):
        if v in (None, "", "None"):
            return ""
        s = str(v).strip()
        return s if s.startswith("$") else f"${s}/mo"

    rows = []
    for c in records:
        rk = rank.get(c["id"], {})
        best = rk.get("best_role") or c.get("best_role_auto", "")
        matched = c.get("role_scores", {})
        row = {
            "Best role": best,
            "Fit (0-10)": rk.get("fit", ""),
            "Why": rk.get("why", ""),
            "Name": c.get("name", ""),
            "Country": c.get("country", ""),
            "Recent title": rk.get("title", c.get("recent_title", "")),
            "English": rk.get("english") or c.get("english_field", "") or "",
            "Salary/mo": salary_fmt(c.get("salary")),
            "FT/PT": rk.get("ft_pt", c.get("ft_pt", "")),
            "YoE": c.get("yoe", "") or "",
            "Last applied role": c.get("last_applied_role", ""),
            "Last applied": c.get("last_applied_date", ""),
            "TT profile": c.get("profile_url", ""),
            "Email": c.get("email", ""),
            "Screening summary": (c.get("summary", "") or "").replace("\n", " ").strip(),
        }
        for rn in role_names:
            row[rn] = "✓" if rn in matched else ""
        rows.append(row)

    # sort: Best role, then Fit desc (blanks last)
    def fit_key(r):
        try:
            return -float(r["Fit (0-10)"])
        except (TypeError, ValueError):
            return 0.0
    rows.sort(key=lambda r: (r["Best role"], fit_key(r)))

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows -> {args.out}")
    print("Drag this CSV into drive.google.com and it opens as an editable Google Sheet, "
          "or upload via a write-enabled Drive connector as a native Sheet.")


if __name__ == "__main__":
    main()
