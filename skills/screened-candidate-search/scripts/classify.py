"""Coarse-classify the screened pool into the target roles and drop irrelevant areas.

Why this is keyword-based and not an LLM pass: the screened pool is ~2,000 people. Running a
model over every one to ask "which of these 4 roles?" is slow and needless — the screening
summaries are keyword-rich, so a cheap match reliably buckets people into role FAMILIES and
throws out the clearly-irrelevant areas (engineering, design, pure marketing, finance...).
That takes ~2,000 down to a few hundred relevant candidates, which is a sane set to then
enrich and hand-rank. The model's judgment is better spent on ranking that short list than on
bulk triage.

A candidate is kept if they hit at least one role's keywords. `exclude` keywords only knock
someone out if they ALSO matched no role (so an "engineer" who reads as a support lead still
survives on the support keywords). Every kept candidate keeps ALL the roles they matched
(the role-matrix in the final sheet), plus a per-role hit count so you can sort by strength.

Config: assets/roles.example.json (copy + edit). Output: work/classified.jsonl.

Usage:
    python3 classify.py --roles roles.json --in work/screened.jsonl --out work/classified.jsonl
"""
import argparse
import json
import pathlib
import re


def load_roles(path):
    cfg = json.loads(pathlib.Path(path).read_text())
    for r in cfg["roles"]:
        r["_pats"] = [re.compile(r"\b" + re.escape(k.lower()) + r"\b") for k in r["keywords"]]
    cfg["_excl"] = [re.compile(r"\b" + re.escape(k.lower()) + r"\b") for k in cfg.get("exclude_areas", [])]
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", required=True)
    ap.add_argument("--in", dest="inp", default="work/screened.jsonl")
    ap.add_argument("--out", default="work/classified.jsonl")
    args = ap.parse_args()

    cfg = load_roles(args.roles)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    kept = 0
    from collections import Counter
    dist = Counter()
    with out.open("w") as fh:
        for line in pathlib.Path(args.inp).open():
            c = json.loads(line)
            hay = (c.get("summary", "") + " " + " ".join(c.get("tags", []))).lower()
            scores = {}
            for r in cfg["roles"]:
                hits = sum(1 for p in r["_pats"] if p.search(hay))
                if hits:
                    scores[r["name"]] = hits
            if not scores:
                continue  # matched no target role -> not relevant
            excl_hits = sum(1 for p in cfg["_excl"] if p.search(hay))
            # excludes only override weak, single-keyword role matches
            if excl_hits and max(scores.values()) <= 1:
                continue
            best = max(scores, key=scores.get)
            c["role_scores"] = scores
            c["best_role_auto"] = best
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
            kept += 1
            dist[best] += 1

    import sys
    print(f"classified (kept): {kept} -> {out}", file=sys.stderr)
    for k, v in dist.most_common():
        print(f"  {v:>4}  {k}", file=sys.stderr)


if __name__ == "__main__":
    main()
