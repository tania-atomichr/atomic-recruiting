# Drafting the client message

The output is a Slack message that presents the shortlist to the client's hiring manager. It is
**always a draft for the recruiter to review and send** — never post it to the client channel
yourself. It's external and irreversible, and the recruiter owns the client relationship.

## First: learn what THIS client values
Different hiring managers care about different things, and they say so across their Slack messages.
Before drafting, search the client's channel and their messages and mine their priorities, then weave
those into the blurbs (and prefer candidates who have them).
- Find the client's channel: `slack_search_channels` on the client's name.
- Read the client contact's own messages: `slack_search_public_and_private` with
  `from:<@THEIR_USER_ID>` and terms, and read the channel where the JD was discussed.
- Capture: must-haves (English level, stack, domain), soft signals (AI-tool fluency, "toughness",
  top-university, quick learner, budget ceiling), and the agreed salary band.

Examples of the SHAPE of client priorities you'll find (mine the real ones from Slack each time):
- A B2B-SaaS hiring manager: quick learner, fluent English, tech/SaaS experience, resilience, and
  **comfort using AI tools (Claude/ChatGPT)** — call a valued trait out explicitly when a candidate
  has it. Note any agreed salary band and stay inside it.
- A creative/marketing client: creative-strategy depth, hook quality, portfolio, US-audience exposure.

To find whether a candidate has a valued trait (e.g. AI usage) without re-reading everything, grep the
candidate's share page / resume-summary for the relevant terms (`AI|Claude|ChatGPT|automation|...`).

## House style (from how atomic shares candidates to clients)
Short and skimmable. Per candidate, one bolded name line + 1-3 sentence blurb with the facts a hiring
manager scans for. Rank by the fit score; lead with genuine fits and be honest about weaker ones
(don't present a sales closer as an onboarding star, or vice-versa).

Template:
```
Hi <Client> 👋 <one-line framing: first batch for the <role> role>. Everyone here has already been
through our screening interview (recording + transcript are on each profile), so they're pre-vetted —
I still need to confirm each person's interest in *this specific* role before we move, but wanted your read.

Ranked by fit<, and I flagged <the trait this client cares about> since I know that matters to you>:

**1. <Name>** — <Country> · <YoE> yrs · ~$<salary>/mo · English <CEFR>
<1-2 sentences: recent role + one concrete, quantified strength + the client-valued trait if present.> <client-safe link>

**2. <Name>** — ...

<Optional: "Also worth a look: <Name> — <one line why, and the caveat>.">

<Honest one-liner about the rest of the pool if relevant.>

What do you think? If any stand out, next step would be a first interview with <client's hiring lead> — want me to line those up?
```

## Rules
- **Draft only.** Present it to the recruiter; ask whether to post / who to include / adjustments.
- Include the **client-safe** share links (Recipe B), never the full ones (which carry recordings/internal docs).
- Every candidate: **based (country), YoE, salary expectation, English (CEFR), one concrete strength.**
- State they're **pre-screened** and that **interest in this role is not yet confirmed**.
- Be candid about fit — the recruiter's credibility with the client depends on not overselling.
- No em dashes, no AI-tells, professional but warm (match the recruiter's own Slack tone, not the client's).
- Propose a concrete **next step** (usually a first interview with the client's hiring lead).
