# tt-post-job — live ids (verified 2026-07-14)

Read anything you are unsure of live (`GET departments`, `roles`, `custom_fields/1773`, `interview_kits?query=`, `GET jobs/659646`). These are the known-stable ones.

## Template
- **Atomic Template job = 659646** (`template:true`, `human_status:template`). Read its stages, triggers, and `location_ids` live at build time.
- Its **13 stages** (name → row_order): Inbox 0, Reviewing 100000, Invitados 200000, Screening 300000, Screening Scheduled 400000, Screening Done 500000, Submit to client 600000, Submitted 650000, 1st Interview 700000, 2nd Interview 800000, Final Round 900000, Offer 1000000, Hired 1100000.
- Its **6 triggers** (read live): message on Invitados ("I think you'd be a good fit - [Role]"), smart-schedule on Screening (organizer 46355, kit 16394, proceed → Screening Scheduled, Google Meet, 30 min, weekdays, 09:00-22:00 Central America), message on Screening Scheduled ("[Role] – Info for Our Upcoming Call"), message + survey on Screening Done ("Thanks again – next steps from here"), todo on Submit to client. Remap organizer/kit/assignee/proceed-stage to the actual role when rebuilding (see build-sequence.md step 3).

## Departments
Product **7963** · Marketing **7964** · Operations & Business **7965** · Sales & Business Development **7962** · Technology/Engineering **7961** · Leadership **7966**.

## Roles (department 7963 Product, others via `GET roles`)
UX/UI Designer **12321** · Product Analyst **12324** · Product Manager **12320** · Product Designer **12322** · UX Researcher **12323** · Technical Product Manager **12325** · Paid Acquisition Specialist **12329** (dept 7964).

## Recruiters (candidate-experience specialists — NEVER Tania)
Do NOT hardcode recruiter names or ids. Fetch live: `GET users?per_page=100` (internal API) returns every user with `id`, `name`, `role`. Ask the user which recruiter owns candidate experience for this role (or take it as input), then match by name to get the id. The template job's current `recruiter_id` (`GET jobs/659646`) is the default when the user has no preference.

## Client custom field = 1773 (Select, REQUIRED on every job PUT)
Do NOT hardcode client option ids. Fetch live: `GET custom_fields/1773` returns every option with its id and value (the client name) — match the role's client by name, case-insensitive. New clients appear automatically once added in TT. `value` in the PUT is the OPTION id as a string in an array, e.g. `["<optionId>"]`, not the label. If the client has no option yet, stop and tell the user to add it in TT settings first (the field is required; an unmatched client blocks the post).

## The 6 canonical ✪ application questions (owned by the application-questions skill)
Location **75227** (mandatory) · English **34786** (mandatory) · Availability **212587** (mandatory) · Salary **35702** (mandatory) · Interest **58122** (mandatory) · Show-your-work **212588** (optional). Role-specific ⌖ questions come from the application-questions skill and attach on top.

## job_detail defaults (from the template)
`reply_time:'two_weeks'`; requirements `name_required` / `phone_optional` / `candidate_location_optional` / `resume_required` / `cover_letter_off` / `additional_files_off`. `remote_status:'fully'`, `employment_type:'fully'`.

## Locations
Do NOT copy the template's 79-city dump. Select ~14 tailored cities per role (4 hubs + overlooked cities across countries, seeded by job id) — full algorithm + safe-PUT in `references/location-selection.md`. Pool: `GET locations?page[size]=300` (plain per_page caps at 50), filter region_id (Latam 1422 ≈ 142 cities). Regions: Latam 1422 · Canada 1423 · US 2600 · EMEA 2630 · APAC 4947.

## Interview kits (examples; find the role's via `GET interview_kits?query=`)
Do NOT hardcode kit ids. Fetch live: `GET interview_kits?query=<role or client>` and match the naming convention `{Role} IK | {Client}`. If only older, off-convention kits exist for the role, post WITHOUT a kit and flag it for the interview-kit skill; do not attach a stale kit silently.

## The two drafts posted 2026-07-14 (this session)
UX Designer **661641**, Product Specialist **661644** — both `draft`, configured, but on TT DEFAULT stages (created before this skill existed). They need the step 2-3 pipeline rebuild to get the Atomic stages + triggers.
