---
name: opp-brief
description: Write a role's Opportunity Brief (OB) and create it INSIDE the role's page in the Notion Open Roles DB. The OB is the candidate-facing brief that NAMES the client (unlike the anonymous public JD) — it is the single source of truth every downstream skill reads (atomic-jd anonymizes it, interview-kit derives questions from it, application-questions derives the ⌖ reality-checks, tt-post-job links it in the Scheduled-stage message). Use for role intake: when a new role lands, after a discovery/intake call, or when the user asks to write an OB / opp brief / opportunity brief / role brief for a role. Takes intake notes, a transcript, or a rough description plus company context; asks for missing critical facts instead of inventing them.
---

# opp-brief — the Opportunity Brief, written into the role's Notion page

The OB is the document a candidate reads before their screening call, and the document every other skill in the pipeline treats as ground truth. It names the client, states real comp guidance, and is honest about constraints. Write it once, well, in the role's page — everything else projects from it.

## Inputs (accept any combination)
- **Intake notes / discovery-call transcript / a rough brief** from the recruiter.
- **The role row** in the Open Roles DB (client relation, practice area, seniority, stage). If no row exists yet, create one (Role, Company relation, Stage "0. New", Status "In progress") and say so.
- **Company context**: an existing company page in Notion, the client's website, app listings, videos. Research the Further Reading links live — do not invent URLs.

**Never invent the critical facts.** Comp range, manager/reporting line, employment type and hours, interview steps, and team size come from the intake or the client. If one is missing, ask (batch the questions, once). Everything else you can draft from research and mark assumptions for review.

## The format — follow `references/format.md` exactly
The 8 sections from the house template (each with the questions it must answer): 1 Overview · 2 About [Company] · 3 About the Role (Scope, Day-to-Day, Key Success Indicators, Challenges, Compensation & Employment) · 4 Ideal Background (+ optional green/red flags screening guidance) · 5 Team, Pace & How They Work · 6 Interview Process · 7 FAQs · 8 Further Reading. Omit a subsection you have no data for rather than padding it.

House conventions that make it an Atomic OB (all in `references/format.md`):
- **Names the client.** The OB is not anonymous. "{Company} is hiring a…", not "our client".
- **The 💡 "Atomic market insight" callout** (purple) right after the Overview: the honest hourly USD market range for similar LATAM searches + an invitation to share their target rate. OBs quote HOURLY (candidates comparing contracts think in rates here); the public JD converts to monthly — that is the JD's rule, not this one.
- **Key Success Indicators** are load-bearing: interview-kit reads them for NUMBERS TO CAPTURE and application-questions derives the ⌖ reality-checks from the core craft. Make them measurable and real.
- **Challenges are stated, not hidden.** Honesty about constraints (connectivity, deadlines, ambiguity, overlap hours) is the house differentiator.

## Voice
Clear, direct, factual, candidate-friendly (the template's own tone checklist): explain **why the role exists** before listing tasks; concrete outcomes and examples; no hype ("rockstar", "fast-paced"); honest about constraints. Bold the key terms candidates scan for (hours, pay cadence, PTO, tools, reporting line). No em or en dashes — commas, colons, parentheses. Simple English.

## Where it goes in Notion (exact write path in `references/notion-write.md`)
**Always inside the role's page** in the Open Roles DB — never the Document Hub, never a loose page:
1. Open the role's page and find its **Tasks Tracker inline database** (the first inline DB; per-role data-source id; title property "Task name"). Create the OB as a page there titled **"Opp Brief - {Role} at {Company}"**.
2. **Fresh "0. New" role pages may have no tracker yet** — fall back to a direct **child page of the role page** (the live UX/UI OB is exactly this), same content.
3. Return the OB URL. Downstream skills (tt-post-job's Scheduled message, interview-kit's instructions) link to it.

## After writing
- Report: the OB URL, the facts you were given vs. researched vs. still open for review.
- Offer the natural next steps in the chain: atomic-jd (anonymized JD) → interview-kit → application-questions → tt-post-job. Do not run them unasked.

## Do not
- Invent comp, managers, metrics, team sizes, or interview steps. Ask.
- Anonymize. That is atomic-jd's job, downstream.
- Put the OB anywhere but inside the role's page.
- Pad a section with generic filler to make it look complete — a short true section beats a long invented one.
