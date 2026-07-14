---
name: atomic-onboarding
description: Onboard a teammate to the atomic-recruiting plugin — check and guide the connections it needs (Teamtailor API key, Notion, Gmail, Chrome logged into Teamtailor), set their own recruiter email, verify each one works, then give a short tour of what the plugin can do and how to use it. Use when someone just installed the plugin, asks "how do I set this up / get started / connect everything", "what can this do", "am I connected", or when a recruiting skill fails because a connection is missing.
---

# atomic-onboarding — get set up, then learn what you can do

Two jobs: **(A) make sure every connection the plugin needs is live**, and **(B) show the teammate what they can now do**. Run A first (fix what's missing), then B.

## A. Connection check (run each, report ✅ / ❌ with the fix)

Go through these in order. For each, actually test it, then tell the user the result and, if it's missing, exactly how to connect it. Do not assume — check.

1. **Teamtailor API key** — the foundation for every data query.
   - Check: is `TEAMTAILOR_API_KEY` set? (`echo $TEAMTAILOR_API_KEY` via Bash, or try a small teamtailor-connect call like "count open jobs").
   - If missing: ask the user for the key (they get it from Tania via a password manager, never Slack/email plaintext), then save it to their `~/.claude/settings.json` `env` block as `TEAMTAILOR_API_KEY` (the update-config skill / a direct settings.json write). Tell them to start a new session for it to load. Warn: pasting the key in chat puts it in that conversation's history — fine for the shared internal key, but not on a screen-share.

2. **Your own recruiter email** — used by candidate-summary and candidate-review-to-client to share candidates to your inbox and read the link back. **Never Tania's; each teammate uses their own.**
   - Check: is `ATOMIC_RECRUITER_EMAIL` set?
   - If missing: ask "which inbox should candidate shares go to?" and save it to `~/.claude/settings.json` `env` as `ATOMIC_RECRUITER_EMAIL`. This must be the same account whose Gmail is connected in step 4.

3. **Notion connector** — for opp-brief, interview-kit, candidate-review-to-client (writing OBs, kits, summaries into the workspace).
   - Check: try a small Notion call (e.g. fetch the Open Roles DB). If the tools aren't available/authed, it's not connected.
   - If missing: tell them to connect Notion to the atomic✳HR workspace via claude.ai connector settings (or `/mcp` in an interactive session). This session cannot run the OAuth flow for them.

4. **Gmail connector** — on THEIR own recruiting inbox (same address as step 2), so candidate-summary can read back the share link.
   - Check: try a small Gmail call (search recent threads). If unavailable/unauthed, not connected.
   - If missing: connect Gmail for their inbox via claude.ai connector settings or `/mcp`.

5. **Chrome logged into Teamtailor** (with the Claude extension) — required by the skills that WRITE into TT: tt-post-job (pipeline build), interview-kit (TT build), application-questions (bank writes), candidate-summary/review (share links). Data-only queries don't need it.
   - Check: `mcp__claude-in-chrome__list_connected_browsers`. If none, or TT isn't open/logged in, flag it.
   - If missing: ask them to open Chrome with the Claude extension and log into Teamtailor (app.teamtailor.com). Do not fall back to desktop control.

**Report as a checklist** so they see exactly what's ready and what to fix:
```
✅ Teamtailor API key
✅ Recruiter email (you@hireatomic.com)
❌ Notion — connect it in claude.ai settings, then re-run setup
✅ Gmail
✅ Chrome + Teamtailor
```
If anything is ❌, they can still use whatever the live connections allow (e.g. API key alone = data queries and spreadsheets), but say which skills won't work yet.

## B. What you can do (the tour — show after setup)

Give a short, concrete tour. The core loop:

> **Post a role, end to end:** intake notes → I write the Opportunity Brief on the role's Notion page → the public JD → the interview kit → the application questions → a fully-configured Teamtailor draft (13-stage pipeline, automations, locations, kit). You review and publish. Then I can seed the job with ~5 vetted Sourced candidates for you to review.

The building blocks, with an example ask for each:
- **opp-brief** — "write the OB for [role] at [client], here are my intake notes…"
- **atomic-jd** — "draft the JD for [role]"
- **interview-kit** — "build the interview kit for [role]"
- **application-questions** — "set up the application questions for [role]"
- **tt-post-job** — "post [role] to Teamtailor" (lands as a DRAFT; you publish)
- **screened-candidate-search** — "find screened candidates for [roles] at [client]" then "add the top ones to the job"
- **candidate-summary** — "write the summary for this candidate" (paste a TT share link or id)
- **candidate-review-to-client** — "prep the review-stage candidates for [client]"
- **candidate-fit-score** — "score this candidate against the [role] brief"
- **teamtailor-connect** — "how many open jobs / candidates do we have?"

**The one rule to tell every new teammate:** the plugin prepares, you decide. Jobs land as drafts (never auto-published), candidates land as Sourced (never advanced or messaged), and missing facts get asked, never invented.

Point them to the full SOP: the Notion Document Hub page "SOP: The atomic✳HR Recruiting Plugin", and the repo README (github.com/tania-atomichr/atomic-recruiting).

## Do not
- Save the API key anywhere shared or committed; it goes only in the user's personal `~/.claude/settings.json`.
- Use Tania's email for anyone else — each teammate's own inbox.
- Claim a connection works without testing it.
