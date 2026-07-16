# Definition-of-Done checklists (the audit gates)

Each phase subagent returns its section with every line PASS/FAIL + one-line evidence. The orchestrator independently re-verifies the lines marked ⚡ with direct GETs. Any FAIL bounces the phase.

## A. opp-brief
- [ ] All 8 sections present (Overview, About Company, About Role w/ Scope+Day-to-Day+KSIs, Ideal Background, Team & Pace, Interview Process, FAQs, Further Reading)
- [ ] NAMES the client (OB is not anonymous)
- [ ] 💡 Atomic market insight callout, HOURLY for OBs
- [ ] KSIs measurable and real (they feed the kit's NUMBERS TO CAPTURE and the ⌖ questions)
- [ ] ⚡ Created INSIDE the role's Notion page (tracker row, or child page on fresh roles)
- [ ] Critical facts (comp, manager, hours, process, market) from intake or ASKED — every assumption flagged in a callout for the user
- [ ] No em/en dashes; no internal-only notes if candidates will see the page

## B. atomic-jd
- [ ] House architecture exactly: Company Overview → Your Role → You'll → You Bring → Bonus Points → What's Offered → Interview Process (real process only). NO invented sections, NO About-Atomic footer, NO cities list in body
- [ ] Title = `Role (qualifier) | context | Remote/On-site (geo) emoji`, pipe-segmented; ⚡ pitch ≤ 200 chars
- [ ] Client-anonymous with truthful metrics kept (years, users, volumes, team size)
- [ ] Comp = Atomic market ESTIMATE + share-your-range invite, in the candidate's pay unit (LATAM monthly / US-hourly hourly). NEVER the client band flat
- [ ] Voice: gold examples' register (example-jd.md; entry-level roles: example-jd-entry-level.md — dignify the work, reassure through structure)
- [ ] Banned-pattern scan clean: no em/en dashes, no rule-of-three, no pivots, no hype words, no snappy word-substitutions (identify not spot, documentation not docs…)
- [ ] Structured block returned (title, internal_name, pitch, body_html, comp_band, region/department/role hints, emojis)

## C. interview-kit
- [ ] ⚡ Name `{Role} IK | {Client}`; built from the LIVE Template ({{TT_TEMPLATE_KIT_ID}}): all 13 ★ canonicals reused BY ID, zero regenerated
- [ ] 🧩 domains: bank-searched first (reuse by id when same intent), discovery voice (📋 LEARNING, no "tell me about a time"), one (Scale) anchor each, script in DESCRIPTION not title
- [ ] Core-skills section inserted after Attitude, before Education; scorecard = Template's 12 + Core skills
- [ ] Instructions: session goals + NUMBERS TO CAPTURE (from OB KSIs) + OB link
- [ ] ⚡ Kit attached to the job AND the smart-schedule trigger points at it
- [ ] Notion backup page inside the role's page (🧩 full scripts + ★ restore-by-id table)
- [ ] No "lean"/simplified format regardless of role type; old kits untouched/hidden, never deleted

## D. application-questions
- [ ] ⚡ All 6 ✪ attached by id with correct flags (location/English/salary/availability mandatory; interest/show-work optional) — none dropped without the user's explicit say-so
- [ ] 2 ⌖ per role, passing the core test: checkable noun/number, retrieval not composition, no answer-key options in the question, no canonical/résumé overlap, answerable by every legitimate persona incl. career-changers
- [ ] Field/entry-level roles: comfortable PROXY at apply (no verification-grade data: license/insurance/docs); consent phrased as openness + the why; hard gates live in the process, not the form
- [ ] Titles short (⌖/✪ prefix), nudges in description
- [ ] ⚡ Question count + flags re-verified by GET after the final write of the phase

## E. tt-post-job
- [ ] Shell via public POST; ⚡ status = draft at the end
- [ ] ⚡ 13 stages in template order (reuse-or-create; names unique; "Screening " trailing space)
- [ ] 6 triggers rebuilt; [Role] substituted in messages AND smart-schedule summary/event_description REWRITTEN with this role's name (they carry old-role text hardcoded)
- [ ] Scheduled-stage message embeds the OB link + local-timezone note; message copy matches the role's register (no LATAM-contractor phrasing on US roles and vice versa)
- [ ] Client option + recruiter + kit resolved by LIVE lookup (recruiter never Tania); ~14 seeded strategic locations (or the role's true markets); hero image ({{TT_HERO_IMAGE_ID}}) copied
- [ ] ⚡ Final GET: question count, kit id, body length, pitch length, client value, location count all correct — and re-checked after any later PUT to the job

## F. screened-candidate-search (inject mode)
- [ ] Judged read of summaries (never keyword-rank alone); full ranked sheet produced BEFORE any injection
- [ ] Gate: fit ≥ 8, no critical-dim gap, defensible one-line why; cap agreed with the user; dedup via filter[job] first
- [ ] sourced:true only; nothing advanced/messaged/rejected; ⚡ post-inject GET confirms count
- [ ] Honest report: pool depth, who was excluded and why (salary/English flags), English-unconfirmed caveat

## G. Final audit (orchestrator, before reporting)
- [ ] Every ⚡ line re-verified with fresh GETs in one pass
- [ ] Assumptions list compiled across phases for the user
- [ ] Links: TT job, OB, kit, Notion backup, sheet
- [ ] What was deliberately NOT done + why
