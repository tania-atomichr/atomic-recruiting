---
name: tt-post-job
description: Post a role to Teamtailor as a fully-configured DRAFT, autonomously carrying the Atomic pipeline. Takes the atomic-jd structured block (title, pitch, body_html, hints) plus the role's client, recruiter, and interview kit, and builds a complete TT job by COPYING the "Atomic Template" job via the internal `new_from_template` endpoint (inheriting stages, automation, questions, hero image, videos, reply/reject emails, and hiring team in one call), then applying per-role edits: JD body, Client, recruiter, salary range, tailored locations, role-corrected trigger texts, kit, and ⌖ questions. Leaves it as a draft for review, never publishes. Use after atomic-jd (and optionally application-questions + interview-kit) when the user wants a role actually posted to / set up in Teamtailor.
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"; external users: see ORG.example.md in the repo). Read that file once at the start and substitute values before using any URL or id. If it's missing, run onboarding first.

# tt-post-job — post a role to Teamtailor as a configured draft

This is the poster: it turns the content skills' output into a real, fully-configured Teamtailor job, on the Atomic pipeline, ready for a human to review and publish. It writes to live Teamtailor, so it is deliberate and it verifies everything.

## What it produces
A **draft** TT job with: the JD (title, pitch, body), the **Atomic 13-stage pipeline and its automation triggers**, the **Client** custom field, the **6 canonical application questions**, the role's **interview kit**, the **LATAM location set**, the assigned **recruiter**, and the standard job-detail settings. Status stays `draft`. It never publishes, and it never deletes anything except stages on the brand-new job it just created.

## Inputs
- The **atomic-jd structured block** (title, internal_name, pitch ≤200, body_html, comp, region_hint, department_hint, role_hint, emojis).
- The **client** (maps to a Client custom-field option id), the **recruiter** (candidate-experience specialist, never Tania), and the **interview kit id** for the role (from interview-kit; if none exists yet, say so and post without a kit rather than attaching a stale one).
- Optionally, the role's **⌖ application questions** from application-questions (attached on top of the 6 canonicals).

## Why it rebuilds the pipeline instead of duplicating the template
The intended path was Teamtailor's "Copy job" on the golden template (job {{TT_TEMPLATE_JOB_ID}} "Atomic Template"), which carries stages + triggers + questions automatically. But that Copy flow is a client-rendered Ember modal that does NOT paint in a headless automation browser, and its submit is not a replayable JSON endpoint (every guessable `jobs/{id}/copy` path returns 404). So the poster instead **reads the template live and rebuilds its pipeline via API**, which is fully verified and has a bonus: it remaps the automation to the actual role (recruiter as organizer, the role's kit, the role's stages) instead of copying the template's placeholders.

## The sequence (full detail in `references/build-sequence.md`)
1. **Create the shell** via the PUBLIC REST API (`POST /jobs`, key from teamtailor_flag.py). Internal `POST jobs` 500s; public create is the one. Returns the new job id; it comes with ~5 default stages.
2. **Swap the stages.** Read the template's 13 stages, DELETE the new job's default stages, CREATE the 13 (name + row_order). Safe because the new job has zero candidates. Keep a name to new-stage-id map.
3. **Rebuild the triggers.** Read the template's triggers, and for each recreate it on the matching new stage: message triggers with `[Role]` replaced by the real role; the smart-schedule/survey/todo triggers with their references remapped (organizer = this role's recruiter, interview_kit = this role's kit, proceed_stage = the new stage id, todo assignee = the recruiter).
4. **Configure the job** with ONE internal `PUT jobs/{id}`: department, role, remote/employment, locations, recruiter, and the nested `job_detail` (body, pitch, reply_time, application requirements, Client custom field, the 6 canonical questions + any ⌖, the interview kit). **Locations are TAILORED, not the full region dump:** ~14 strategic cities (4 hubs + overlooked cities round-robined across countries), deterministically seeded by job id so roles don't stack on the same set — algorithm and safe-PUT recipe in `references/location-selection.md`.
5. **Verify** every field with GETs and report counts. Never trust a 200.

After a successful post, offer the natural follow-on: **screened-candidate-search** can seed the new job with a quality-gated shortlist (fit ≥ 8, capped ~5) injected as Sourced candidates for the recruiter to review — its step 8. Offer it; do not run it unasked.

## Non-negotiables
- **Draft only. Never publish.** Publishing is the recruiter's decision. Leave `status:draft`.
- **Verify, do not trust.** After every write, GET and check counts (stages = 13, questions = 6 + ⌖, kit present, client set, body/pitch non-empty). The internal PUT full-replaces nested collections and job_detail fields, so a missing field silently nulls. `references/build-sequence.md` lists every landmine.
- **Client is required** in every PUT or you get 422. **body and pitch live on job_detail** and null if omitted. Pitch ≤ 200 chars.
- **Recruiter is a candidate-experience specialist, never the AM.** Fetch the user list live and ask which recruiter owns this role (recipe in `references/ids.md`); never hardcode names or ids.
- **Read the template live** (job {{TT_TEMPLATE_JOB_ID}}) for stages and triggers rather than trusting hardcoded copies, so the poster follows the template if it changes.
- **Archive, never delete** real jobs. The only deletes allowed are the fresh job's own default stages in step 2.

## Do not
- Publish, or set anything past `draft`.
- Attach a stale interview kit just to fill the slot. No current kit = post without one and flag it for interview-kit.
- Invent ids. Read them live (`GET departments`, `roles`, `custom_fields/1773`, `interview_kits?query=`) when unsure; `references/ids.md` has the known-stable ones.
