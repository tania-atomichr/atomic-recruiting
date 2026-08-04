---
name: tt-post-job
description: Post a role to Teamtailor as a fully-configured DRAFT, autonomously carrying the Atomic pipeline. Takes the atomic-jd structured block (title, pitch, body_html, hints) plus the role's client, recruiter, and interview kit, and builds a complete TT job by COPYING the "Atomic Template" job via the internal `new_from_template` endpoint (inheriting stages, automation, questions, hero image, videos, reply/reject emails, and hiring team in one call), then applying per-role edits: JD body, Client, recruiter, salary range, tailored locations, role-corrected trigger texts, kit, and ⌖ questions. Leaves it as a draft for review, never publishes. Use after atomic-jd (and optionally application-questions + interview-kit) when the user wants a role actually posted to / set up in Teamtailor.
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"; external users: see ORG.example.md in the repo). Read that file once at the start and substitute values before using any URL or id. If it's missing, run onboarding first.

# tt-post-job — post a role to Teamtailor as a configured draft

This is the poster: it turns the content skills' output into a real, fully-configured Teamtailor job, on the Atomic pipeline, ready for a human to review and publish. It writes to live Teamtailor, so it is deliberate and it verifies everything.

**Drift guard:** if you are deep in a long session and this file's rules are not verbatim in your recent context, re-read this file AND `references/build-sequence.md` before any TT write. Memory of a skill is not the skill.

## What it produces
A **draft** TT job with: the JD (title, pitch, body), the **Atomic 13-stage pipeline and its automation triggers**, the **Client** custom field, the **6 canonical application questions**, the role's **interview kit**, the **LATAM location set**, the assigned **recruiter**, and the standard job-detail settings. Status stays `draft`. It never publishes, and it never deletes anything except stages on the brand-new job it just created.

## Inputs
- The **atomic-jd structured block** (title, internal_name, pitch ≤200, body_html, comp, region_hint, department_hint, role_hint, emojis).
- The **client** (maps to a Client custom-field option id), the **recruiter** (candidate-experience specialist, never Tania), and the **interview kit id** for the role (from interview-kit; if none exists yet, say so and post without a kit rather than attaching a stale one).
- Optionally, the role's **⌖ application questions** from application-questions (attached on top of the 6 canonicals).

## COPY-FIRST architecture (v2). The job is a COPY of the template, then per-role edits.
Copy the golden template with the internal endpoint **`POST jobs/{{TT_TEMPLATE_JOB_ID}}/new_from_template`** (`{params:{job_name:"<title>"}}`) → the new job inherits EVERYTHING in one call: the 13 stages, 6 automation triggers, 6 ✪ questions, hero image, videos, reply/reject emails, hiring team, and locations. Rebuilding from zero and replicating piece-by-piece is the LEGACY fallback (documented in build-sequence.md) — it caused a long tail of missed pieces; use it only if the copy endpoint breaks.

## The sequence (full detail in `references/build-sequence.md`)
1. **Copy the template** (`new_from_template`, internal API from the logged-in tab). Verify inheritance: 13 stages, 6 triggers, 6 questions, 2 videos, image, reply/reject emails.
2. **Per-role configuration** in ONE full-echo PUT: title/internal_name, department, role, recruiter (live lookup), remote status, salary range (market estimate, candidate's pay unit), the JD body + pitch on job_detail, the Client option (live lookup), and REPLACE the inherited 79 locations with the ~14 tailored ones (`references/location-selection.md`). Set `status:'draft'` (the copy arrives as "temp").
3. **Per-role trigger + email edits** (the copy inherits template texts): substitute `[Role]` in the 3 messages; REWRITE smart-schedule `summary`/`event_description` + remap organizer/kit/proceed-stage; embed the role's Notion **OB child page** link in the Scheduled message; substitute the role name in `reply_body`/`reject_body`; todo assignee = recruiter.
4. **Attach the role's kit and ⌖ questions** (interview-kit + application-questions skills).
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
