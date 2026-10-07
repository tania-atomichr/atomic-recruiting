---
name: interview-kit
description: Build a role's interview kit end to end — analyze the JD/Opportunity Brief, author ONLY the role-specific Core Skills questions (reusing existing bank questions when an equivalent exists; everything canonical is reused by id), publish the kit page inside the role's page in the Notion Open Roles DB, and create the kit in Teamtailor starting from one of the two base kits, "Template" (v1) or "Template v2" (the user chooses). Use when the user wants an interview kit, screening script, discovery questions, or an interview guide for a role. Produces content AND does the Notion + Teamtailor writes.
---

> **Token resolution:** ids/urls written as `{{TOKEN}}` are org config, resolved from `~/.claude/atomic-recruiting-org.md` (created by atomic-onboarding's "set me up"; external users: see ORG.example.md in the repo). Read that file once at the start and substitute values before using any URL or id. If it's missing, run onboarding first.

# interview-kit — from role brief to live Teamtailor kit

The standard kit is a solved problem: the 13 ★ canonical questions (intro, story, the ✳️ optionals for transitions/environments/business/education, scope, signals, curiosity & AI, motivation, logistics, wrap-up, verdict) live in the **Teamtailor bank**, pre-assembled in the kit template named **"Template"** (kit id {{TT_TEMPLATE_KIT_ID}}), every question carrying its skill, every kit selecting all 11 areas + Conclusion. The reasoning is documented in the Hub SOP ("Interview Kits: structure, canonical questions, and how to build one" — https://app.notion.com/p/{{NOTION_IK_SOP}}). This skill therefore authors **only the role-specific 🧩 Tailored Domains** and then does the assembly: a Notion page inside the role's tracker and a real kit in Teamtailor built from the live Template.

## Step 0 — which template? (ask before anything else)
There are TWO base kits in Teamtailor and the recruiter chooses. If the request doesn't already say which, ask once, with both options, and wait for the answer:

| | **Template (v1)** | **Template v2** |
| --- | --- | --- |
| Kit | named exactly `Template`, id {{TT_TEMPLATE_KIT_ID}} | named exactly `Template v2` (resolve the id live by name: `GET interview_kits?template=true&dont_show_hidden=false&per_page=25&page=N`; use {{TT_TEMPLATE_V2_KIT_ID}} if the org file has it) |
| Canonicals | 13 ★ questions, unnumbered titles | 12 ★ questions titled `★ 1. Opening \| v2` … `★ 11. Wrap-up \| v2` + Final Recommendation |
| Section 5 (Core skills, the 🧩 role questions) | authored by this skill (Parts 1–2) | taken from the role's kit in the portal web app (Part 2-v2); authored here only when the portal has none |
| Where Core skills sits | after Attitude, before Education | after Seniority (`4. Your work there`), before Attitude (`6. What you're known for`) — the empty slot the template already carries |
| Instructions box | session goals + NUMBERS TO CAPTURE + links | fill the template's own skeleton (role details, key screening points, numbers to capture, legend, links) |

Never mix the two: a v2 kit carries only `| v2` canonicals, a v1 kit only the v1 ones. State the chosen template in the Part 1 planning block and in the final summary. Everything below applies to both unless a line says v1 or v2.

Never regenerate the canonical slots. Rewriting "Tell me about yourself" per role is how the bank ended up with 7 Motivations. Reuse by id, always.

## ⛔ PRE-WRITE GATE — hard rules that survive even if you read nothing else
No Teamtailor write happens until all three hold:
1. **The kit is built FROM the live base kit the user chose in Step 0 (`Template` {{TT_TEMPLATE_KIT_ID}} or `Template v2`)** — all ★/✳️ canonicals reused by id, zero regenerated, same skeleton for every role type (entry-level and field roles included; "lean" kits are forbidden).
2. **Bank search BEFORE creating any 🧩 question — with evidence.** Internal API `GET questions?query=<topic keywords>&per_page=25` (or a Teamtailor MCP connector's `list_questions`). You may not POST a new question unless the search query and its result ids appear in THIS conversation. A sibling role's equivalent found = reuse that id.
3. **Kit `instructions` are set at CREATE time, never edited after** — a post-create instructions PUT wipes picked_questions + scorecard (live incident 2026-07-16; restore recipe in `references/tt-build.md`).

**Drift guard:** if you are deep in a long session and these rules are not verbatim in your recent context, re-read this file before the write step. Memory of a skill is not the skill.

**No role type is an exception — never hand-compose a "lean" or "simplified" kit.** Entry-level, field, gig, hourly, and on-site roles use the SAME Template skeleton as everyone else (proven live: a Property Inspector gig kit, 2026-07-15). What adapts per role: the 🧩 Tailored Domains (e.g. Field Work & Reliability, Documentation & Detail, Resident Interaction instead of engineering domains), the session goals, and the NUMBERS TO CAPTURE. What never changes: the ★ canonicals by id, the section layout, the naming (`{Role} IK | {Client}`), the instructions block, and the Notion backup page. The ✳️ optional canonicals are the built-in mechanism for lighter screens — the recruiter skips them organically; you do not delete them. If a kit feels "too heavy" for a role, that is a conversation with the user, not a license to invent a new format.

Work in four parts. Read the reference for each part before doing it. Order: Part 1 → Part 2 → **Part 4 (build in TT)** → **Part 3 (Notion full-text backup, written LAST** — it snapshots the finished kit's real ids, order, and live scripts). Parts are numbered by topic, not run order.

**The soul of the kit — never lose this:** discovery, not evaluation. Questions must not sound like a test; they help the candidate talk openly about what they have done, how they worked, what environments they've been in, and what they want next. Warm, curious, confidence-building. This kit is **Stage 1 only**: gather a clear picture so someone else can decide later. Scoring, fit, and rubrics live elsewhere. The full conversation always covers: intro, career story, company & industry context, scope of work, working practices, the tailored domains, signals of strength, motivation, practical details, optional bonus areas, wrap-up, and recruiter notes — the canonical skeleton carries most of these; the tailored domains are what this skill writes.

## Part 1 — Information goals (`references/information-goals.md`)
Read the JD / Opportunity Brief / Notion role page. Produce **6–8 neutral, fact-seeking information goals** covering the full picture of the candidate's background (tools, projects, products, systems, workflows, environments) — never evaluative. Then mark each goal **[canonical]** (a standard question already harvests it) or **[tailored]** (feeds Part 2). Show the goals as a short planning block for a sanity check, then continue.

## Part 2 — Author the Tailored Domains (`references/role-questions.md`)
From the tailored-marked goals, write **3–6 experience areas with 2–4 soft, pattern-based questions each** (fewer domains for simple roles), plus pick which optional canonical slots this role needs. The wording rules in the reference are non-negotiable: no test phrasing, no quoting the JD, ownership learned through "where did your role usually start and end", never through challenges.

## Part 2-v2 — Section 5 comes from the portal (Template v2 only)
On a v2 kit the 🧩 questions are the ones the team already sees on the role in the portal (finds.hireatomic.com), so the kit and the web app say the same thing. Do not author your own first.
1. Find the role with the portal connector (`list_roles` / `search`), then `get_role` → its `interview_kit` (themes, each with questions and follow-ups).
2. No kit drawn yet → `draw_interview_kit` (role_id; preview first, then commit). Never pass `redraw=true` unless the user asks: a redraw replaces the team's hand edits.
3. One 🧩 question per portal THEME, in the portal's order: title `🧩 {Theme name}`, body = a `📋 LEARNING:` line + that theme's questions and follow-ups VERBATIM. Do not reword, add, drop, or re-split them; if something reads wrong, say so and let the user fix it in the portal (`edit_interview_kit`) first.
4. Bank search still applies (gate 2): a 🧩 question from an earlier build of the same role with the same text is reused by id.
5. Portal connector unavailable, or the role isn't in the portal → tell the user, and only with their OK fall back to authoring per Part 2. Say in the final summary which source section 5 came from.
Part 1 still runs on v2: its goals feed the instructions box (key screening points, numbers to capture).

## Part 3 — Publish a FULL-TEXT backup to Notion, inside the role (`references/canonical-kit.md` for the skeleton)
The kit page lives **inside the role's page in the Open Roles database** (`collection://{{NOTION_OPEN_ROLES_DATA_SOURCE}}`), NOT in the Document Hub. Every role page contains an inline per-role docs/tasks database (the first inline database on the page, the "Tasks Tracker" family — each role has its own data-source id, so resolve it at runtime): fetch the role page, take the first inline database's `data-source-url`, fetch that data source for its schema, then create the kit page there with the title property (`Task name`) = `Interview Kit — {Role}`.

**This page is a complete standalone backup** — the whole kit must be readable and restorable from Notion alone, even if the TT kit is deleted. Build it AFTER Part 4 (so you have the final question ids and the exact assembled order), by reading the finished TT kit's rendered order and every question's live `description`. Page content, in order:
1. **Header** — links to the live TT kit + the SOP, the kit's tags, and a dated line: "Full-text snapshot as of {date} — canonical scripts are snapshots; the source of truth is the TT question by id."
2. **Role analysis** — the Part 1 information goals with their [canonical]/[tailored] marks.
3. **The full call script, every question in kit order** — for EACH question (canonical ★/✳️ and role 🧩 alike): its title, its `#id`, its skill/trait, and its **complete verbatim script** pasted from the live TT `description`. Put the ~13 canonical scripts under a collapsed/"snapshot" heading and the role-specific 🧩 questions under their own heading with the extra reasoning line (what it extracts, reused #id vs newly created). Divider lines (the `___` runs) can be collapsed to a single rule for readability.
4. **Rebuild note** — one line: canonical questions restore from the Template; 🧩 questions restore from this page's verbatim text (recreate via POST with the skill + `interview kit`/client/role tags).

If the user gives a role name but no page, find the role in Open Roles first; if no role page exists, say so and fall back to asking where to put it.

## Part 4 — Build in Teamtailor (`references/tt-build.md`)
Through the logged-in Teamtailor tab (Chrome MCP), in this order: **first search the bank for each authored question** — an equivalent may already exist from a sibling role; reuse its id instead of creating (this is mandatory, not a courtesy: duplicates are how the bank rotted). Only then create the genuinely new questions (🧩-prefixed titles, tagged Core Skills), create the kit from the chosen base kit's live content, placing the Core-skills section (the role's 🧩 questions) where that template puts it per `canonical-kit.md`'s layout recipe: **v1** between Signals of Strength and Education & Learning; **v2** in the empty Core-skills slot between `4. Your work there` and `6. What you're known for`. Name it `{Role} IK | {Client}`, tag the kit with the client + practice area, and fill the kit's instructions box (the interviewer's cheat sheet): **v1** = the Part 1 session goals plus links to the Opportunity Brief and the Notion kit page; **v2** = the Template v2 skeleton with every `{placeholder}` filled from the brief (no braces left), plus the same links and the portal role link. Verify by GET **and** by rendering the kit edit page (the layout uses section `children` order — see the reference). Attach to the job via the job's Evaluation tab. The reference has the exact endpoints, headers, and the full-replace landmine — do not write to kits without reading it.

## Inputs
A JD, an Opportunity Brief, a Notion Open Roles page, or a role title plus notes. Fetch the Notion page if referenced. Also take: client name (needed for naming), the target TT job if it exists (for attaching), and optional notes on what to emphasize.

## Non-negotiables
- Canonical slots are reused by id, never rewritten. If a canonical script needs improving, that's an edit to the canonical (propagates everywhere), raised separately — not a per-role fork.
- Search the bank before writing any new question; the question may already exist from a sibling role.
- Every new question gets: a **`🧩 {Topic}`** title (the puzzle-piece marks role-specific; NO role or client name in the title — those go in tags), the full script in the body opening with a `📋 LEARNING:` line (follow-up chain included — compressing scripts measurably loses facts), the **skill it feeds** (Core Skills in most cases; Domain when it probes the business model), and tags: **`interview kit`** + **client** + **role** (lowercase). Title convention: ★ = always-on canonical, ✳️ = optional canonical, 🧩 = role-specific.
- Archive, never delete, anything in Teamtailor.
