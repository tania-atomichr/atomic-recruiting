# tt-post-job — the exact build sequence

Two API surfaces:
- **Public REST** (`https://api.na.teamtailor.com/v1/`): job CREATE only. Header `Authorization: Token token=<KEY>` (KEY in `teamtailor_flag.py`, or `TEAMTAILOR_API_KEY`), `X-Api-Version: 20240904`, `Content-Type: application/vnd.api+json`. JSON:API shape `{data:{type,attributes,relationships}}`.
- **Internal app API** (`https://tt.na.teamtailor.com/app/companies/{{TT_COMPANY_ID}}/api/`): everything else, from a logged-in Chrome tab. Headers `{Content-Type:application/json, X-Requested-With:XMLHttpRequest, X-Ember-Route:jobs.job.edit.index}` + `credentials:'include'`. Cross-origin fetch from an `app.teamtailor.com` tab works. Rails shape `{job:{...}}` / `{stage:{...}}` / `{trigger:{...}}`, NOT `{data}`.

Run steps 2-3 (stage/trigger writes) as a single detached routine; they are ~25 calls. GET after each phase and verify before moving on.

## 1. Create the shell (public REST)
`POST /v1/jobs` with `{data:{type:'jobs', attributes:{title, body:'<placeholder>', pitch:pitch.slice(0,200), status:'draft', 'remote-status':'fully'}, relationships:{user:{data:{type:'users',id:RECRUITER}}, department:{data:{type:'departments',id:DEPT}}, role:{data:{type:'roles',id:ROLE}}}}}` → 201, returns `data.id` = new job id. (Internal `POST jobs` → 500; do not use it to create.) The new job arrives with ~5 default stages (Inbox/Reviewing/Interview/Offered/Hired).

## 2. Swap stages (internal) — SAFE only on the brand-new job (zero candidates)
- Read template: `GET stages?job_id={{TT_TEMPLATE_JOB_ID}}` → sort by `row_order`. The 13: Inbox(0), Reviewing(100000), Invitados(200000), Screening(300000), Screening Scheduled(400000), Screening Done(500000), Submit to client(600000), Submitted(650000), 1st Interview(700000), 2nd Interview(800000), Final Round(900000), Offer(1000000), Hired(1100000).
- Read the new job's current stages: `GET stages?job_id=NEW` (fresh jobs have ~5 defaults: Inbox, Reviewing, Interview, Offered, Hired).
- **LANDMINE — stage names are unique per job.** `POST stages` for a name that already exists (Inbox/Reviewing/Hired collide with the defaults) → 422. Use **reuse-or-create** (proven 2026-07-14 on both live drafts):
  - For each template stage: if a current stage with the same trimmed name exists, REUSE it and fix its position: `PUT stages/{id} {stage:{id, job_id:NEW, name, row_order:<template row_order>}}` → 200. Otherwise CREATE: `POST stages {stage:{job_id:NEW, name, row_order}}` → 201.
  - Build the map `stageNameToNewId[name]` from both paths.
  - Then DELETE every current default whose name is NOT in the template list (`DELETE stages/{id}` → 204; e.g. Interview, Offered).
  - Create-before-delete ordering means the job never has zero stages.
- Verify `GET stages?job_id=NEW` returns 13 in template row_order.
- Beware the template's "Screening " has a TRAILING SPACE — always compare `name.trim()`.

## 3. Rebuild triggers (internal)
- Read all triggers `GET triggers?per_page=200` and filter to the template's stage ids (the `?job_id=` filter is IGNORED, so filter client-side by `stage_id ∈ template stage ids`). The template carries 6: three `message`, one `smart-schedule`, one `survey`, one `todo`.
- For each template trigger, find the new stage by the template stage's NAME → `stageNameToNewId`, then `POST triggers`:
  - **message**: `{trigger:{type:'trigger/message', kind:'message', stage_id:newStageId, subject, body, platform:t.platform||'email', on_reject:!!t.on_reject, delay_job_for:t.delay_job_for||0, delay_job_for_unit:t.delay_job_for_unit||'minutes'}}`. Replace every `[Role]` in subject and body with the real role title. Template messages: Invitados "I think you'd be a good fit - [Role]", Screening Scheduled "[Role] – Info for Our Upcoming Call", Screening Done "Thanks again – next steps from here".
  - **smart-schedule** (on Screening): carries `organizer_id`, `user_ids`, `interview_kit_id`, `proceed_stage_id`, `has_video`, `provider_name`, `duration`, `from_time`/`to_time`, `time_zone`, `weekdays`, `buffer`, `start_interval`, `timeframe`, `required_attendees`, `event_description`, `summary`. Recreate with `organizer_id` and `user_ids` = this role's RECRUITER, `interview_kit_id` = this role's kit, `proceed_stage_id` = the new "Screening Scheduled" stage id, and copy the scheduling mechanics verbatim. **LANDMINE (missed live on 3 jobs): `summary` and `event_description` carry the OLD role's name HARDCODED (no `[Role]` token) — find-replace misses them. Always REWRITE both with this role's name** (`summary` = "{Role} Discovery Call"; event_description = the booking invite the candidate reads).
  - **Scheduled-stage confirmation message MUST embed the role's Notion OB link** (Tania's standing design): after the what-to-expect paragraph, add "If you'd like more detail before we talk, here's the full role brief: <a href='OB_URL'>{Role}, everything about the role</a>" + a "the calendar invite shows your local time zone" note. The OB page must be SHARED TO WEB in Notion (a UI click, not possible via API — flag it to the user), and must contain no internal notes/callouts since candidates read it.
  - **survey** (on Screening Done): carries a `form_id`; copy it. If the survey form is generic, reuse the template's `form_id`.
  - **todo** (on Submit to client): carries `assignee_id`; set it to this role's recruiter.
- Verify the new job's triggers: re-`GET triggers` and count those whose `stage_id ∈ new stage ids`.
- **ALL SIX trigger types verified live 2026-07-14** (both drafts, every POST → 201): 3 message (with `[Role]` substitution landing in subject+body), smart-schedule (organizer/user_ids/kit/proceed_stage all remapped and confirmed by GET), survey (form_id copied), todo (assignee remapped). The exact POST bodies used are in this file's shapes above.

## 4. Configure the job — ONE internal PUT
`PUT jobs/{NEW} {job:{ department_id, role_id, remote_status:'fully', employment_type:'fully', location_ids:[...79 LATAM...], recruiter_id, pitch, job_detail:{ body, pitch, reply_time:'two_weeks', name_requirement:'name_required', phone_requirement:'phone_optional', candidate_location_requirement:'candidate_location_optional', resume_requirement:'resume_required', cover_letter_requirement:'cover_letter_off', additional_files_requirement:'additional_files_off', picked_custom_fields_attributes:[Client], picked_questions_attributes:[6 canonical + any ⌖], picked_interview_kits_attributes:[kit] } }}`.
- **LANDMINE — body/pitch:** they live on `job_detail` and the PUT full-replaces job_detail, so ALWAYS include `job_detail.body` and `job_detail.pitch` or they null (200, blank).
- **LANDMINE — Client required:** `picked_custom_fields_attributes:[{custom_field_id:1773, field_type:'CustomField::Select', type:'CustomField::Select', name:'Client', owner_id:NEW, owner_type:'Job', value:['<optionId>'], lid:uuid()}]`. Omit it and every PUT 422s "Client can't be blank". `value` is the OPTION id, not the label.
- **LANDMINE — full-replace nested collections:** send the COMPLETE `picked_questions_attributes` array every time. New rows use `lid:crypto.randomUUID()`; existing rows use their real `id` (read first with `GET job_details/{jobDetailId}`). To DROP a picked row (e.g. removing a question), send `{id:<rowId>, _destroy:true}` (verified works 2026-07-14).
- **COVER IMAGE (fresh-POST jobs lose it) — copy it explicitly.** A public-POST job has NO hero image; the template's lives at `job_detail.image_with_setting.picked_image.image` (the "Job Hero Background.png", **image id 109692**). Set it in the configure PUT: `job_detail.image_with_setting_attributes:{id:<job's own iws id, from GET job_details>, picked_image_attributes:{image_id:109692, row_order:0}}`. Without this the posting looks blank/unbranded (Tania noticed immediately). Read the template's current picked_image id live in case the hero image changes. Also the template carries 2 `picked_videos` — copy those the same way if a role should have them.
- `location_ids` = read them live from the template (`GET jobs/{{TT_TEMPLATE_JOB_ID}} → job.location_ids`, the 79-city LATAM set) and reuse.
- Get `job_detail_id` from `GET jobs/{NEW} → job.job_detail_id` for the kit's `job_detail_id` field.

## 5. Verify
`GET jobs/{NEW}` + `GET job_details/{jobDetailId}` + `GET stages?job_id={NEW}` + trigger count. Confirm: status `draft`; stages = 13; questions = 6 (+⌖); kit present; client set (`formatted_value` = the client name); body/pitch non-empty; no em/en dashes in body if that matters for the JD. Report the counts. If anything is wrong, STOP and show the user; do not paper over it.

## Cleanup / safety
- `DELETE jobs/{id}` works (204) but policy is ARCHIVE, not delete, for anything real. The only deletes this skill performs are the fresh job's own default stages in step 2.
- If a build fails midway, the half-built draft is safe to leave (it is a draft) or archive; never leave it published.
