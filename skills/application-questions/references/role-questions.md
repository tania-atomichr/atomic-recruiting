# The ⌖ role-specific reality-check — authoring logic

This is the only thing this skill writes. It occupies **one slot**: the concrete craft reality-check. Guard it hard against drifting into canonical or résumé territory.

## The one job
Prove that a **specific, hands-on craft is real and recent**. Neither the canonical set nor the résumé gives us that reliably. A résumé can list "React Native, 5 years"; a two-line reality-check exposes whether they actually shipped it. That is the entire purpose. Not motivation, not availability, not seniority, not "why this role." Just: **what did you actually last do, and with what.**

## The anti-overlap check (run on every draft; if it re-covers any of these, DROP it)
- ❌ pay / hours / location / timezone / availability → **canonical (Logistics)**
- ❌ English / communication → **canonical**
- ❌ "why do you want this" / motivation → **canonical (interest)**
- ❌ "share your portfolio" (generic) → **canonical (show your work)**
- ❌ years / seniority / education / career path → **the résumé already shows it**
- ✅ keep only: a **specific, recent, hands-on detail** that proves the work is real

A role question is never about wanting the job, being available, or how senior they are. It is *"what did you actually last build/run/ship, and with what tool."*

## How to author it (the intelligence)
From the brief's core craft, ask:

> **"What's the one thing an experienced [role] answers in two seconds that a faker or a bot can't produce?"**

That is a version, a tool plus how it was used, a specific technique or output, or a number they'd know cold. Then:

- **THE CORE TEST — the answer is a checkable noun or number, never composed prose.** Every canonical example's answer is a proper noun or figure with an external referent: "RN 0.73", "Meta + Google, ROAS", "Zendesk, ~60/day", "QuickBooks, accrual". The candidate RETRIEVES the answer; they do not write it. If the natural answer is a free-form phrase or a process description ("the onboarding flow", "annotated specs with edge cases"), the question fails: an LLM composes flawless prose, but it has no ground truth for stack facts not on the résumé, so facts filter and prose does not. Corollary: never ask a question whose model answer appears in articles about the craft ("what does a good handoff include?") — that tests reading, not doing.
- **Anchor the TOOL LAYER, not the abstract layer.** Every real practitioner lives in a nameable tool/platform/system with nameable numbers. This is also how you handle an OR-list background (e.g. "product, ops, implementation, or support"): do not retreat to something abstract everyone shares ("what product did you work with") — find the tool-shaped common denominator (everyone in that OR-list lives in SOME tracker/ticketing system and knows their weekly volume). If the question would make a qualified candidate from any OR-branch say "I haven't", it tests the wrong thing.
- **Never embed answer-shaped examples in the question.** Listing options in the question ("…Figma Dev Mode, Zeplin, annotated PDFs, something else?") hands the AI and the faker the answer key — it is multiple choice with extra steps, and it defeats the open-text tell. Ask bare ("What does your engineering handoff usually go out in?") and let the specificity of the answer do the filtering.
- **Design for the CAREER-CHANGER who is actually a fit.** Before finalizing, enumerate the real candidate personas — including domain experts converting into the role (the customer themselves: e.g. a property manager moving into product for a property-inspection SaaS is often the STRONGEST candidate, not an edge case). If the question strands one legitimate persona ("what tracker were you in" strands the PM who lived in AppFolio, not Jira), drop one level of abstraction to the layer everyone truly shares ("what software did you spend most of your day in at your last job") — still a noun answer, and the noun itself tells you which world they come from.
- **One anchor per question.** A second clause is allowed ONLY as a qualifier of the same recall ("what ticketing system were you last in, **and roughly what daily volume**"), never a second separate recall ("what tool… and what was the last flow you shipped" = two questions in one, confusing).
- **The answer must be recall, not composition.** "What version were you shipping?" is recall (2 seconds). "What's one edge case you designed around?" is composition (a minute and a paragraph) — that is an interview question, not an application question. If answering requires choosing a story, drop it.
- **Anchor it on most recent / last role / in production.** This makes it real and easy to answer honestly ("in my last role I was on…"), and it dodges the résumé-summary voice a bot falls into.
- **Open text.** Never a picker. A picker lets a bot click the right answer; open text is where generation shows itself (verified live: on an RN role, an open "what version" question had 47% give a real version, 23% self-admit "I haven't worked in RN", and bots paste "The resume does not specify…" verbatim — over half the field filterable from one low-friction question).
- **2 per role.** Two sharp questions covering two different facets of the craft (e.g. the tool/version reality-check + the output/number reality-check). Never a third — the form must stay short. Drop to 1 only when the role genuinely has a single craft surface and a second question would forcibly overlap the first.

## Logistics requirements (entry-level / field / on-site roles) — ask the COMFORTABLE PROXY, verify later
Some roles have hard logistics requirements (a car + license, a background check, work authorization, being in a market). The form still only ASKS — it never verifies. Two rules, learned live (Tania, 2026-07-14):

- **Never request verification-grade personal data at apply time**: license status, insurance, documents, IDs. That reads as an interrogation and kills conversion with exactly the nervous entry-level applicants you want. Ask the 2-second comfortable proxy instead, and let the description say verification comes later:
  - ❌ "What vehicle would you use? Include whether your license and insurance are current." (a data grab)
  - ✅ "How would you get around for your property visits?" desc: "Most of our technicians use their own car. Nothing to send or verify now, that comes later in the process."
- **Phrase consent as openness + the why, never as a pass/fail prediction**:
  - ❌ "Are you able to pass a background check?" (implies suspicion, makes them self-judge)
  - ✅ "Would you be comfortable with a standard background check later on?" desc: "You would be visiting occupied and vacant homes, so we run one before training. Nothing needed now."
- The hard gate lives in the PROCESS (the logistics-check step after screening), not in the form. Avoid `is_qualifying` on these unless the user asks for auto-knockout — TT pins qualifying questions FIRST on the form, which makes the very first thing a candidate sees a gate (cold).
- At most 1-2 of these per role, additive to (never replacing) the canonicals.

## NEVER drop canonicals when adapting a role type
Adapting to an unusual role (US/on-site/entry-level/gig) means adjusting FLAGS and wording emphasis, not removing canonical questions. If a canonical seems irrelevant (English for a US role, portfolio for entry-level), ASK the user before dropping it — the default is all 6 attached. Hand-composing a question set without re-reading this skill is how forms drift off-spec.

## Tone (match the canonical set)
Warm, concrete, low-friction, with an easy honest out. A real practitioner answers in seconds; a non-fit finds it easy to say "I haven't."

**Never** use these — they are test / gate / résumé phrasings:
- "Describe your experience with…"
- "Rate your…" / "On a scale of…"
- "How many years…"
- "Do you have experience with…"

## Worked examples (the recipe, right tone, no overlap)
- **Dev:** "In your most recent React Native work, what version were you shipping to production?"
- **Paid media:** "What ad platforms were you last running campaigns in, and one metric you watched day to day?"
- **SDR:** "What outreach tool were you last using, and what did a normal day of activity look like?"
- **Support:** "What ticketing system were you last in, and roughly what daily volume?"
- **Bookkeeper:** "What accounting software were you last working in, and what kind of books — size or complexity?"

Each proves the craft, none touches comp / logistics / motivation / years, all leave room for an honest "I haven't."

## TITLE vs DESCRIPTION
Keep the **title short** (the spoken question). A long title breaks the web form layout. Put any clarifying nudge in the **description**, not the title. Tag the skill **Core skills (67334)**; tags `application` + client + role (reuse exact existing spellings, don't mint duplicates).
