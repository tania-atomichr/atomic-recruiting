# Conversion benchmarks + the feedback loop

Derived from the atomic✳HR Teamtailor data (Jan–Jul 2026, ~150 postings with page views). Use this to judge whether a JD is good, and to know what to optimize.

## Two levers, measured two different ways
- **Title → views (reach) and audience match.** Views swing with reach, freshness, and which board a post landed on, so they are noisy. The clean way to test a title is an A/B in Teamtailor (the team already runs TEST A / TEST B), then read views. Do not over-tune titles from historical numbers; apply the structure rules and test.
- **JD body → conversion (applications ÷ views).** This is the reliable signal. It reproduces within ~1 point across reposts of the same JD (e.g. a Video Editor role held 12.0–12.4% while its views ranged 233 to 2,754). So conversion is what to optimize the body against, and it is trustworthy even on a single post.

## Conversion is NOT driven by seniority
Junior 11.4%, Mid 11.3%, Senior+ 11.65% across the whole dataset (under 0.4 points apart). Do not assume senior or niche roles convert worse. Judge every role against its family and client baseline instead.

## Baselines — judge a JD relative to these, not to a global number

By role family (median conversion):
| Family | median | typical range |
|---|---|---|
| Engineering | 13.0% | 11–15% |
| Ops / Admin | 11.9% | 10–16% |
| Product / Design | 11.9% | 12–13% |
| Sales / BD | 11.1% | 8–14% |
| Marketing | 10.6% | 9–12% |
| CS / Support | 9.6% | 9–11% |

By client (brand/appeal effect, ~6 point spread): **the per-client baseline table is internal data and lives in the Notion Document Hub page "JD conversion baselines by client (internal)" (`39da97e2-3bc3-81dd-bdbe-d8f6b488c96c`)** — fetch it when judging a JD. It is deliberately not in this repo.

A JD is "good" when it clears the blend of its family baseline (above) and its client baseline (the Notion table). Strong-brand clients run several points above weak-brand ones, so never judge against a single global number.

## The feedback loop (how the system improves on any client or role)
1. Draft the JD to the rules in `format.md`.
2. Post it and let it run.
3. Read its conversion from Teamtailor and compare to the family+client baseline here.
4. If it is below baseline, revise the body (shape-fast structure, tighter bullets, self-selecting voice, concrete offer) and, if the title may be pulling the wrong audience, A/B a more accurate title and watch views.
5. Feed repeat winners and losers back into these rules.

This loop is role- and client-agnostic, which is what makes it a system rather than a one-off.
