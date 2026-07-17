# Writing the OB into Notion — the exact path

The OB always lives **inside the role's page** in the Open Roles DB. Never the Document Hub, never a workspace-level page.

## The databases
- **Open Roles DB**: database `{{NOTION_OPEN_ROLES_DB}}`, data source `collection://{{NOTION_OPEN_ROLES_DATA_SOURCE}}`. Role rows carry: Role (title), Company (relation), Stage (0. New → 9. Closed), Status, Practice Area, Seniority, Sourcer, AM.
- Each role PAGE contains inline databases. The **first inline DB is the per-role Tasks Tracker** — its data-source id is DIFFERENT per role (resolve at runtime by fetching the role page and reading the first `<database inline="true" data-source-url="collection://…">`), and its title property is **"Task name"**.

## Create sequence
1. **Find (or create) the role row.** Query the Open Roles data source by Role name. If it does not exist, create it with `notion-create-pages` (parent = the Open Roles data source) with Role, Company relation, Stage "0. New", Status "In progress" — and tell the user you created it.
2. **Fetch the role page** and look for the Tasks Tracker inline DB.
   - **Tracker exists** → create the OB as a page in the tracker (parent = the tracker's data-source id), title property "Task name" = **"Opp Brief - {Role} at {Company}"**. (This is where the house template itself lives on other roles.)
   - **No tracker yet** (fresh "0. New" pages often have none) → create the OB as a **direct child page of the role page** (parent = page_id), title "{Role} at {Company}" or "Opp Brief - {Role} at {Company}". The live gold-standard OB (a UX/UI Designer brief, Notion id {{NOTION_GOLD_OB_EXAMPLE}}) is exactly this: a child page of the role page. Do NOT create a tracker yourself.
3. **Write the content** with Notion-flavored markdown: `##` headings for the 8 numbered sections, the 💡 callout as `<callout icon="💡" color="purple_bg">`, bold key terms, bullet lists. One page, no sub-pages.
4. **Verify**: fetch the created page back, confirm the sections rendered and the parent is the role page (or its tracker). Return the URL.

## Templates and examples (read, never edit)
- House template: `{{NOTION_OB_TEMPLATE}}` ("Template Opp Brief - Role Name at Company Name").
- Gold-standard live OB: `{{NOTION_GOLD_OB_EXAMPLE}}` (a UX/UI Designer brief).
- Example role page with trackers: `{{NOTION_EXAMPLE_ROLE_PAGE}}` ("Mid Level/Sr Automation Engineer").

## Gotchas
- The tracker's data-source id is per-role — never hardcode one role's tracker id for another role.
- Multi-source queries need Enterprise; query ONE data source at a time.
- Companies live in their own DB (relation on the role row); link the existing company page, don't duplicate it.
- After creating, the OB URL goes to: tt-post-job (the Scheduled-stage message embeds it) and interview-kit (kit instructions link it). Mention both when handing off.

## THE SHARE STRUCTURE (hard rule, learned live 2026-07-16)
The role page is INTERNAL (properties, trackers, comments, IK backup). The OB is **its own child page** and is **the ONLY page ever shared or linked to candidates**. Never:
- link candidates (TT messages, kit instructions) to the ROLE page — it exposes trackers, counts, and the interview-kit backup;
- nest the interview-kit page inside the OB — a public OB share exposes every subpage, leaking interview questions;
- leave the OB inline on the role page body when it will be shared — create the dedicated OB child first and link THAT.
Correct tree: Role page → [Opp Brief - {Role} at {Company}] (public-shareable) + [Interview Kit - {Role}...] (internal sibling).
