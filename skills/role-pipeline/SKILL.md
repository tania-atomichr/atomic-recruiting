---
name: role-pipeline
description: Orchestrate the full new-role pipeline end to end (OB → JD → interview kit → application questions → Teamtailor posting → optional candidate injection) by delegating EACH phase to a fresh subagent that reads that phase's skill first, then auditing every artifact against the skill's Definition-of-Done checklist before the pipeline advances. Use when the user wants a role done "end to end", "full cycle", "post the role and set up everything", or names several phases at once. This exists because inline multi-step execution drifts from the skills; orchestrated phases with checklist gates do not.
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"). Read it once at the start.

# role-pipeline — phase-isolated orchestration with checklist gates

## Why this skill exists (read this, it is the operating principle)
When one session executes many phases inline, the skill instructions read early get buried and later steps get hand-composed from memory — canonicals get dropped, tones drift, "lean" kits get invented. The countermeasure is structural, not willpower:
1. **Each phase runs in a FRESH subagent** (the Agent tool) whose prompt orders it to read the phase skill's SKILL.md and every references/*.md BEFORE acting, execute ONLY that phase, and return the artifact + the filled checklist.
2. **The orchestrator audits, it does not create.** You (the orchestrator) never write JD copy, questions, or kits yourself. You verify returned artifacts against `references/checklists.md`, pass or bounce them, and hand context to the next phase.
3. **A phase that fails its checklist is re-run with the failures named** before the pipeline advances. Two failures on the same phase → stop and show the user.

## The pipeline
```
0. Intake        confirm role, client, geography, role type (LATAM-remote | US-field | other), what exists already
1. opp-brief     → OB inside the role's Notion page          [gate: checklist A]
   ⏸ USER GATE: Tania approves the OB (assumptions resolved) before anything reads from it
2. atomic-jd     → JD + structured block                     [gate: checklist B]
3. interview-kit → kit in TT + Notion backup                 [gate: checklist C]
4. application-questions → 6 ✪ + 2 ⌖ on the job              [gate: checklist D]
5. tt-post-job   → fully configured DRAFT                    [gate: checklist E]
6. (on request) screened-candidate-search → judged inject    [gate: checklist F]
7. Final audit: re-GET everything, one report to the user
```
Phases 2-4 all read the OB; never let a later phase "improve" an earlier artifact silently — bounce it back to that phase instead.

## How to delegate a phase (the prompt shape)
**Resolve the skills root FIRST (installs differ — never assume `~/.claude/skills`):** this file you are reading lives at `<skills-root>/role-pipeline/SKILL.md`. Take the directory two levels up from it as `<skills-root>` — every sibling skill lives there (`<skills-root>/<skill>/SKILL.md`). This works identically for loose installs and plugin installs on any machine. Pass ABSOLUTE paths to subagents; a subagent that guesses a path and finds nothing will improvise from memory, which is the exact failure this skill exists to prevent.

Spawn with the Agent tool, one phase at a time (they share the TT browser session, so sequential, never parallel):
```
You are executing ONE phase of the atomic-recruiting pipeline: <phase>.
FIRST load the phase skill — read <skills-root>/<skill>/SKILL.md and EVERY file in
<skills-root>/<skill>/references/ (absolute paths above; if the Skill tool is available to you,
invoking the skill by name is equivalent for SKILL.md, but the references still need explicit reads).
List the files you loaded in your report. If you cannot read them, STOP and return the error —
do NOT proceed from memory. Follow them exactly; where your instinct and the skill disagree,
the skill wins. Do not touch anything outside this phase.
Inputs: <role, client, OB url, ids, prior artifacts>.
When done, return: (a) the artifact/ids/urls, (b) the checklist from
<skills-root>/role-pipeline/references/checklists.md section <X> with every line marked PASS/FAIL
+ one-line evidence, (c) the list of skill files you actually read, (d) anything you had to assume.
```
**A phase report that omits (c) or lists fewer files than the skill's references/ contains is an automatic bounce** — treat it exactly like a checklist FAIL.
Include the role-type flag (LATAM-remote / US-field / entry-level) in every phase prompt — the skills carry explicit rules for these; the flag stops improvisation.

## Auditing (the orchestrator's real job)
- Re-verify the 3-5 highest-risk lines of each checklist YOURSELF with a direct GET (question count + flags, kit id on job + scheduler, body length, title pattern, draft status). Do not trust a subagent's own PASS on those.
- After ANY later write to the same job, re-check the question count and body length again (the post-write-read race and the full-replace landmines are the two silent destroyers).
- The final report to the user shows the per-phase checklist results, every assumption made, and the links (TT job, OB, kit, Notion pages). Flag what was NOT done and why.

## Hard rules inherited from everything learned so far
- Jobs stay DRAFT; candidates land as Sourced only; nothing publishes, messages, or advances.
- Missing critical facts (comp, manager, market, process) are ASKED at intake, never invented mid-phase.
- No role type is an exception to any skill. Unusual role = same skeletons, adapted register/domains/flags, and the adaptation rules are IN the skills.
- Archive, never delete; full-echo on every job PUT; verify after every write.
