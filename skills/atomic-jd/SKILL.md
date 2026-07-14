---
name: atomic-jd
description: Draft a public, client-anonymous job description in the atomic✳HR house style and voice from an Opportunity Brief, a Notion Open Roles page, or a rough brief. Produces both a review-ready JD and a structured block a poster skill can push to Teamtailor, LinkedIn, or job boards. Use when the user wants to write, draft, create, or rework a JD / job post / job ad for a role, or turn an OB or intake brief into a posting. Content only — it does not post anywhere.
---

# atomic-jd — write a job description in the atomic✳HR house style

Turn a brief into a finished public JD: client-anonymous, in the Atomic voice, in the Atomic-JD format, ready to hand to a poster. This skill writes the content. It does not post it anywhere — posting to Teamtailor is a separate skill you compose after this one.

## Inputs (accept any)
- A **Notion Open Roles page or Opportunity Brief** (a URL or id). Fetch it and read Sections 1–8: role, seniority, the client's real business, responsibilities, requirements, comp band, remote/location, interview process, and any metrics.
- A **pasted brief** or bullets or free text.
- A **minimal ask** (just a role title plus a few facts).

If a Notion role or OB is referenced, fetch it first. If information is missing, infer sensible generic defaults ("Fully Remote", "Full-time", "Multiple locations") and keep phrasing generic. Never invent metrics or a client name. Ask at most **3** questions, and only when a real blocker exists (for example, no role title at all). Otherwise proceed.

## Non-negotiables

1. **Client-anonymous.** Never name the client, its product, or identifying brand names. Open the company section with "Our client is a …". Generalize named integrations and features ("integrates with the major property-management platforms", not the vendor names; "a recent AI feature that turns voice into reports", not the product name). Keep the *truthful metrics* the brief gives you (users, years in market, volumes, team size) — those make it credible without identifying anyone. The title's context slot is a generic industry label ("Property Inspection SaaS"), never the client name. The **internal name** may name the client, since it is internal only.

2. **The Atomic voice.** Read `references/voice.md` and write to it. Dense, analytical, conversational, natural, a little nerdy, in simple English. Empathetic, service-oriented, quietly funny in a dry way that lives in the phrasing rather than in jokes. The Atomic-JD format calls itself "marketing-forward" — read that as *compelling through specificity and precision*, not through promotional adjectives or slogans. When the format and the voice conflict, the voice wins.

3. **Run the banned-pattern scan before returning.** `references/voice.md` has the full checklist. The ones that bite in JDs: no em or en dashes anywhere (— –), no rule-of-three flourishes, no "not X, it's Y" pivots, no negative parallelism ("no X, no Y"), no promotional or inflated tone, no vague intensifiers, no abstract appreciation nouns. Fix every hit before you hand anything back.

4. **Respect the poster's constraints.** `pitch` must be **≤ 200 characters** (Teamtailor rejects longer). The title carries **1–3 on-brand emojis**. The body is delivered as **HTML**.

5. **Write for the candidate, in their terms.** This is the one that makes a JD land. Lead with what the reader cares about and can picture: the craft, the kind of problems they will solve, the autonomy, the pay, remote and flexibility. Do not assume the reader cares about or knows the client's industry. Treat the domain as context, not the headline, and keep domain familiarity in Bonus Points. A workflow designer wants complex flows to untangle; they do not need to love property management to want this job, so lead with the flows and mention the field later. Name things the way the candidate names them (their craft, their tools, their title-adjacent language), and translate concrete work into scenes they recognize ("the phone in someone's hand in the field, then the review screen back at the office"). Every line should answer "why would the person reading this care", not "what do we want to say".

6. **Localize compensation to how the reader is actually paid.** For LATAM contractors on a full-time role, quote the range in **USD per month**, because that is how they think about pay, not per hour. If the brief gives an hourly band, convert it: monthly ≈ hourly × weekly-hours × 4.33, then round to a clean range. State the contractor setup and the rough hours basis, keep it a range, and tie it to experience. Mention pay cadence (for example paid weekly in USD) separately from the size of the range.

7. **Optimize for conversion, and know the benchmark.** The body's job is to convert viewers into applicants. Read `references/benchmarks.md` for what "good" is (it varies by role family and client, not one global number) and for the conversion rules proven on the data: give the role a shape fast (group into focus areas only when it is natural, and never invent proportions; a tight plain list is fine), keep bullets tight (~5 per section), use an opinionated self-selecting voice, and make the offer and team context concrete. Do not assume seniority changes conversion; it does not.

## Format
Follow the Atomic-JD structure in `references/format.md` exactly, omitting a section when there is no data for it rather than inventing one. `format.md` also holds the title structure (for views + audience match) and the "body that converts" rules; `benchmarks.md` holds the conversion baselines and the post → measure → revise feedback loop.

## Output — return both

**A) A review-ready JD** in markdown, so a human can read and edit it.

**B) A structured block** the poster consumes (this is the seam between this skill and the TT poster — keep the field names stable):

```yaml
title:          # public: "Role (specialty) | context | Remote (geo) <emoji>" — see format.md
internal_name:  # internal only, may name the client: "Role (Client)"
pitch:          # the hook, ≤ 200 characters
body_html:      # Company Overview … through Interview Process, as HTML (NO About-Atomic footer — the site adds it automatically)
comp_band:      # Atomic market ESTIMATE, monthly USD, e.g. "$2,800–$4,200 USD/month (estimate, not client band)"; null if none
region_hint:    # LATAM | Americas | US | ... (for the poster to map to a TT region)
department_hint:# e.g. Product, Technology/Engineering, Marketing
role_hint:      # e.g. UX/UI Designer, Product Analyst
emojis:         # the 1–3 used in the title
```

## Process
1. Gather the brief (fetch the Notion page if one is referenced).
2. Draft each section in the Atomic voice, anonymized.
3. Run the banned-pattern scan from `references/voice.md`. Rewrite every hit.
4. Check: `pitch` ≤ 200 chars, title has an emoji, zero em/en dashes anywhere, no triads or pivots.
5. Return the review-ready JD and the structured block.

## Do not
- Post anywhere. Handing off to the poster is a separate step the user runs after reviewing.
- Name the client, or invent facts. If the brief does not state a metric, an interview process, or a benefit, omit that section rather than making it up. The interview process in particular must come from the brief or the role's real Teamtailor pipeline, never from imagination.
- Add commentary or "here's what I changed" inside the JD itself. If the user asked for a rewrite, return the JD, not a description of it.
