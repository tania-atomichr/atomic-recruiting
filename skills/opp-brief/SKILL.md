---
name: opp-brief
description: Fill a role's Opportunity Brief (OB) IN THE CLIENT PORTAL, through the portal connector (get_brief / draft_brief / fill_brief / set_market_insight). The OB is the candidate page the portal serves at /ob/<token>; it is the one source every downstream skill and the sourcing app read. Use for role intake: when a new role lands, after a discovery/intake call, or when the user asks to write an OB / opp brief / opportunity brief / role brief for a role. Takes intake notes, a transcript, or a rough description plus company context; asks for missing critical facts instead of inventing them. Never writes to Notion.
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"; external users: see ORG.example.md in the repo). Read that file once at the start and substitute values before using any URL or id. If it's missing, run onboarding first.

## Where the OB lives now (2026-10-27): the client portal, nowhere else

The portal is the one writer of every search document. This skill no longer creates pages in Notion; `references/notion-write.md` is retired. Work through the **Client Portal connector** (`mcp__Client_Portal_new__*`), as the recruiter:

1. **Find the search**: `search` / `list_roles`, then `get_role` (requirements = `brief`, the client's approval flag, the ideal candidate, criteria) and `get_client` (the company page and its research).
2. **Put the sources on the search**, never in a document: the call or intake notes go through `attach_transcript` / `edit_role` (the role's `brief` box holds the client's JD or requirements). The portal's company research runs on its own once the client is opened; do not research the company again.
3. **Draft**: `draft_brief` writes the eight sections from the requirements, the call, the research and the ideal candidate profile. Then `get_brief` and read it with `references/format.md` beside you. Fix what is wrong with `fill_brief` (one section at a time, preview first, then `preview=false`).
4. **Pay**: the OB shows the **Atomic market insight only** (`set_market_insight`), never the client's budget. Hourly for LATAM contractor searches. The old rule "states real comp guidance" is gone: the portal's rule wins.
5. **Open questions** for the client are the brief's own "What we still need from <client>" list in the portal; answer them there or let the AM send them. Never invent comp, manager, metrics, team size or interview steps.
6. **Return** the brief's state from `get_brief` and the live candidate-page links from `get_role.candidate_page_links` (a sourcing link is made for each sourcer automatically; the Share step on the brief page makes an applicants link). Downstream: atomic-jd, interview-kit, application-questions and tt-post-job all read the portal, not this conversation.

Everything below about the format and the voice still applies; everything about Notion does not.

# opp-brief — the Opportunity Brief, filled in the client portal

**Drift guard:** `references/format.md` (the 8-section template) must be read in THIS conversation before writing. If they aren't in your recent context, read them now.

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

## Where it goes: the client portal, nowhere else
The brief lives on the search in the portal (`get_brief` / `fill_brief`); the candidate reads it at the `/ob/<token>` links in `get_role.candidate_page_links`. Return those links. Downstream skills (tt-post-job's Scheduled message, interview-kit's instructions) link the portal page, never a Notion page.

## After writing
- Report: the OB URL, the facts you were given vs. researched vs. still open for review.
- Offer the natural next steps in the chain: atomic-jd (anonymized JD) → interview-kit → application-questions → tt-post-job. Do not run them unasked.

## Do not
- Invent comp, managers, metrics, team sizes, or interview steps. Ask.
- Anonymize. That is atomic-jd's job, downstream.
- Put the OB anywhere but inside the role's page.
- Pad a section with generic filler to make it look complete — a short true section beats a long invented one.
