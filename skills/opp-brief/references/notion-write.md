# Writing the OB into Notion — the exact path

The OB always lives **inside the role's page** in the Open Roles DB. Never the Document Hub, never a workspace-level page.

## The databases
- **Open Roles DB**: database `{{NOTION_OPEN_ROLES_DB}}`, data source `collection://{{NOTION_OPEN_ROLES_DATA_SOURCE}}`. Role rows carry: Role (title), Company (relation), Stage (0. New → 9. Closed), Status, Practice Area, Seniority, Sourcer, AM.
- Each role PAGE contains inline databases, including the per-role **Tasks Tracker**. Its data-source id is DIFFERENT per role, so resolve it at runtime — but **do not just take "the first inline database"** (see the multi-source trap below).

## ⛔ TEMPLATES ARE THE STRUCTURE — never create a bare page
Both rows this skill creates come from **Notion page templates**. A row created without its template is a blank page: no icon, no Tasks Tracker, no Candidate Submissions, and no "Opp Brief - Role Name at Company Name" row to fill in — so the OB has nowhere correct to live. Resolve every template **by NAME at runtime**, never by a hardcoded id: the per-role tracker (and therefore its templates) has different ids on every role. (Learned live 2026-08-03 on a Data & Analytics Specialist role, fixed by hand.)

## Create sequence
1. **Find (or create) the role row.** Query the Open Roles data source by Role name.
   If it does not exist, create it with `notion-create-pages` (parent = the Open Roles data source) **passing `template_id` = the data source's `default_page_template`** (the template named **"New Role"**) along with Role, Company relation, Stage "0. New", Status "In progress" — and tell the user you created it. Read `default_page_template` live off the Open Roles data source; if it is missing, fetch the data source's templates and match the one named "New Role" rather than proceeding template-less. **A role row created without the template is wrong — delete/redo it rather than working around it.**
2. **Resolve the Tasks Tracker, then create the OB row from ITS template.**
   - **Fetch the DATABASE object, not just the page's inline tag.** The Tasks Tracker block is a **multi-source database**: a blank placeholder data source PLUS the real "Tasks Tracker" source (schema: Task name / Status / Assignee). The page's inline `<database …>` tag surfaces only one of the two collection ids, and it is often the placeholder. Fetch the database and pick the data source **whose name is "Tasks Tracker"** and whose schema has the `Task name` title property. Never assume the first one.
   - **Create the OB row from that data source's "Opp Brief" page template** (pass its `template_id`), with title property `Task name` = **"Opp Brief - {Role} at {Company}"**. Resolve that template id inside the resolved data source at runtime; it differs per role.
     **MATCH THE TEMPLATE NAME LOOSELY — the stored name has irregular whitespace.** Live on 2026-08-04 it reads `"Opp Brief - Role Name at Company Name "` (double space before "at", trailing space). An exact-string match FAILS. Normalize before comparing: trim, collapse runs of whitespace to one, compare case-insensitively — or simply take the template whose name starts with "Opp Brief". The tracker's `default="true"` template is **"New task"**, so a create without an explicit `template_id` silently gets the wrong template. Sibling templates you will see and must not pick: "New task", "Intake Meeting", "Client requirements summary".
   - **No tracker at all** (rare now that step 1 applies the template) → the role row was created without its template. Fix step 1 first. Only if the tracker genuinely cannot exist, fall back to a **direct child page of the role page** (parent = page_id) titled "Opp Brief - {Role} at {Company}", and say so in your report. The live gold-standard OB ({{NOTION_GOLD_OB_EXAMPLE}}) is that child-page shape.
3. **Write the content** with Notion-flavored markdown: `##` headings for the 8 numbered sections, the 💡 callout as `<callout icon="💡" color="purple_bg">`, bold key terms, bullet lists. One page, no sub-pages.
4. **Verify**: fetch the created page back and confirm (a) the 8 sections rendered, (b) the parent is the role page's Tasks Tracker (or the role page), and (c) **the template actually applied** — a new role page shows its icon + the Tasks Tracker and Candidate Submissions blocks, and the OB row carries the template's structure rather than being blank. A blank result means a `template_id` was missed; redo it, do not patch by hand. Return the URL.

## Templates and examples (read, never edit)
- House template: `{{NOTION_OB_TEMPLATE}}` ("Template Opp Brief - Role Name at Company Name").
- Gold-standard live OB: `{{NOTION_GOLD_OB_EXAMPLE}}` (a UX/UI Designer brief).
- Example role page with trackers: `{{NOTION_EXAMPLE_ROLE_PAGE}}` ("Mid Level/Sr Automation Engineer").

## Gotchas
- The tracker's data-source id is per-role — never hardcode one role's tracker id for another role. The same is true of its page templates: resolve **by name**, per role.
- **Notion template names carry stray whitespace** (like TT's "Screening " stage). Verified live 2026-08-04: the OB template is stored as `"Opp Brief - Role Name at Company Name "`. Always normalize (trim + collapse inner runs + case-insensitive) or prefix-match; never `===` a template name.
- **The Tasks Tracker is multi-source.** Two data sources are linked in that one block (verified live: a placeholder literally named **"New data source"** with a bare Name/Status/Assign schema, plus the real **"Tasks Tracker"**). Reading the page's inline `<database>` tag gives you only one collection id and it may be the placeholder — fetch the database object and match on the source NAMED "Tasks Tracker" with the `Task name` schema.
- Multi-source QUERIES need Enterprise; query ONE data source at a time. (Fetching a multi-source database to enumerate its sources is fine — that is not a cross-source query.)
- Companies live in their own DB (relation on the role row); link the existing company page, don't duplicate it.
- After creating, the OB URL goes to: tt-post-job (the Scheduled-stage message embeds it) and interview-kit (kit instructions link it). Mention both when handing off.

## THE SHARE STRUCTURE (hard rule, learned live 2026-07-16)
The role page is INTERNAL (properties, trackers, comments, IK backup). The OB is **its own child page** and is **the ONLY page ever shared or linked to candidates**. Never:
- link candidates (TT messages, kit instructions) to the ROLE page — it exposes trackers, counts, and the interview-kit backup;
- nest the interview-kit page inside the OB — a public OB share exposes every subpage, leaking interview questions;
- leave the OB inline on the role page body when it will be shared — create the dedicated OB child first and link THAT.
Correct tree: Role page → [Opp Brief - {Role} at {Company}] (public-shareable) + [Interview Kit - {Role}...] (internal sibling).
