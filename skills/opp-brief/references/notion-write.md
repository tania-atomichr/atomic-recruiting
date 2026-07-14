# Writing the OB into Notion — the exact path

The OB always lives **inside the role's page** in the Open Roles DB. Never the Document Hub, never a workspace-level page.

## The databases
- **Open Roles DB**: database `25aa97e2-3bc3-809a-82e7-cf30f05f23af`, data source `collection://25aa97e2-3bc3-8078-8b81-000bffbf1ee6`. Role rows carry: Role (title), Company (relation), Stage (0. New → 9. Closed), Status, Practice Area, Seniority, Sourcer, AM.
- Each role PAGE contains inline databases. The **first inline DB is the per-role Tasks Tracker** — its data-source id is DIFFERENT per role (resolve at runtime by fetching the role page and reading the first `<database inline="true" data-source-url="collection://…">`), and its title property is **"Task name"**.

## Create sequence
1. **Find (or create) the role row.** Query the Open Roles data source by Role name. If it does not exist, create it with `notion-create-pages` (parent = the Open Roles data source) with Role, Company relation, Stage "0. New", Status "In progress" — and tell the user you created it.
2. **Fetch the role page** and look for the Tasks Tracker inline DB.
   - **Tracker exists** → create the OB as a page in the tracker (parent = the tracker's data-source id), title property "Task name" = **"Opp Brief - {Role} at {Company}"**. (This is where the house template itself lives on other roles.)
   - **No tracker yet** (fresh "0. New" pages often have none) → create the OB as a **direct child page of the role page** (parent = page_id), title "{Role} at {Company}" or "Opp Brief - {Role} at {Company}". The live gold-standard OB (a UX/UI Designer brief, Notion id 27fa97e2-3bc3-80b1-bba8-f1aca7b000d8) is exactly this: a child page of the role page. Do NOT create a tracker yourself.
3. **Write the content** with Notion-flavored markdown: `##` headings for the 8 numbered sections, the 💡 callout as `<callout icon="💡" color="purple_bg">`, bold key terms, bullet lists. One page, no sub-pages.
4. **Verify**: fetch the created page back, confirm the sections rendered and the parent is the role page (or its tracker). Return the URL.

## Templates and examples (read, never edit)
- House template: `341a97e2-3bc3-8033-929e-e8e84dd84004` ("Template Opp Brief - Role Name at Company Name").
- Gold-standard live OB: `27fa97e2-3bc3-80b1-bba8-f1aca7b000d8` (a UX/UI Designer brief).
- Example role page with trackers: `37ba97e2-3bc3-8042-8eb0-d07e6c70dd31` ("Mid Level/Sr Automation Engineer").

## Gotchas
- The tracker's data-source id is per-role — never hardcode one role's tracker id for another role.
- Multi-source queries need Enterprise; query ONE data source at a time.
- Companies live in their own DB (relation on the role row); link the existing company page, don't duplicate it.
- After creating, the OB URL goes to: tt-post-job (the Scheduled-stage message embeds it) and interview-kit (kit instructions link it). Mention both when handing off.
