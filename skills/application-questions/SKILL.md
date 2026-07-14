---
name: application-questions
description: Author a role's Teamtailor APPLICATION-FORM questions — reuse the 6 canonical ✪ questions by id (never rewritten) and author 2 role-specific ⌖ "reality-check" questions from the brief's core craft (each proving a different facet), then write them to the job via the internal TT API. A reality-check is one tight, open-text "what did you last use / ship / run" that a real practitioner answers in two seconds, a faker or bot can't produce, and a non-fit can honestly opt out of. Use when setting up or fixing the application/screening questions on a Teamtailor job, or when a poster needs the per-role question set. This is the APPLICATION-FORM sibling of interview-kit (which builds the interview kit) — for the short apply form, use THIS.
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"; external users: see ORG.example.md in the repo). Read that file once at the start and substitute values before using any URL or id. If it's missing, run onboarding first.

# application-questions — the apply-form question set for a role

The application form has two competing jobs: stay short (every extra field costs applicants) and still extract signal + filter bots and non-fits. It solves that with a fixed canonical spine reused across every role, plus a tiny role-specific tail. This skill authors the tail and writes the whole set to the job.

## The set = 6 canonical ✪ (reused by id) + at most 1-2 role-specific ⌖

- **Canonical ✪** — the 6 questions every role uses, reused **by id, never rewritten**. They own pay, logistics, English, motivation, and the generic portfolio ask. See `references/canonical-set.md` for the ids, the mandatory flags, and the scorecard mapping. You do not author these. You attach them.
- **Role-specific ⌖** — **2 per role**, authored from the brief's core craft, each covering a different facet (e.g. tool/version + output/number). This is the only slot you write. See `references/role-questions.md` for the authoring logic. Get this wrong and the form bloats or double-covers the canonicals.

## The ⌖ role question has ONE job

The **concrete craft reality-check**: the one thing neither the canonical set nor the résumé reliably gives us, which is *whether this specific, hands-on craft is real and recent*. Nothing else. Not motivation, not availability, not seniority. Just: **what did you actually last do, and with what.**

Before writing any role question, run the anti-overlap check in `references/role-questions.md`. If a draft re-covers pay / hours / location / timezone / English / "why this role" / generic portfolio / years / seniority / education / career path, it belongs to a canonical or the résumé already shows it. **Drop it.** Only a specific, recent, hands-on detail survives.

## Process

1. **Read the brief** (Notion Open Roles page / OB, or the pasted brief). Find the role's core craft: the actual hands-on work, the tools, the outputs, the numbers a practitioner lives in.
2. **Derive the ⌖.** Ask: *"what does an experienced [role] answer in two seconds that a faker or a bot can't produce?"* A version, a tool + how it was used, a specific technique or output, a number they'd know cold. Anchor it on **most recent / last role / in production**. Open text. Warm, low-friction, with an easy honest out. See `references/role-questions.md` for the tone rules and worked examples. Write **2**, each proving a different facet of the craft.
3. **Search the bank first (mandatory).** A ⌖ for this exact craft may already exist. `references/tt-write.md` has the search. Same intent = reuse the id, do not mint a near-duplicate.
4. **Write to Teamtailor.** Create only genuinely-new ⌖ questions (internal API — the public API is read-only for questions, 403 on write), then attach the full set (6 ✪ + the ⌖) to the job's application form with the right mandatory flags. `references/tt-write.md` has the exact calls, the ids, and the full-replace landmine.
5. **Verify.** GET the job_detail back and confirm the picked-questions count and flags. Never trust the 200.

## Mandatory flags
Mandatory: English, location, salary, availability, **and the role reality-check(s)**. Optional (`mandatory:false` on the job's picked_question, not the bank question): interest, show-your-work. Details in `references/canonical-set.md`.

## Anti-bot / fit reading is a SEPARATE step
This skill AUTHORS and ATTACHES the questions. Reading the answers to flag bots and non-fits (no-link, résumé-in-third-person, leaked AI phrasing, duplicate answers, has-the-detail) happens after submission and is not this skill's job. When a ⌖ is a true hard gate (a genuine must-have), mark it `is_qualifying` so TT auto-knocks-out — but default is off.

## Do not
- Rewrite, retitle, or re-tag a canonical ✪. They are shared across every role; reuse by id.
- Author more than 2 role questions, or write one that re-covers a canonical or the résumé.
- Use test/gate/résumé phrasing ("Describe your experience with…", "Rate your…", "How many years…", "Do you have experience with…"). A real one answers in seconds and lets a non-fit say "I haven't."
- Mint client/role tags that already exist — reuse exact spellings.
