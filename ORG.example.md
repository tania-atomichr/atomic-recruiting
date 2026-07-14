# Org config — fill this to run the plugin against YOUR systems

The skills in this repo reference org-specific values as `{{TOKENS}}` so the framework stays portable
and no internal identifiers live in the repo. At runtime, skills resolve tokens from a local file:

```
~/.claude/atomic-recruiting-org.md
```

**atomic✳HR team:** don't fill this by hand. Say **"set me up"** — the onboarding skill reads the
internal Notion config page and writes the resolved file for you.

**Everyone else:** copy the table below into `~/.claude/atomic-recruiting-org.md` and fill your own
instance's values (discover them from your Teamtailor and Notion — each token says where to look).
Numeric record ids you'll meet elsewhere in the docs (question ids, scorecard ids, stage names) are
also instance-specific: treat them as the PATTERN and map your own equivalents.

| Token | Where to find yours |
| --- | --- |
| TT_COMPANY_ID | In any Teamtailor URL: `app.teamtailor.com/companies/<THIS>/...` |
| TT_TEMPLATE_JOB_ID | Build a "golden template" job carrying your standard stages, triggers, and application questions; use its id |
| TT_TEMPLATE_KIT_ID | Your canonical interview-kit template's id (Settings → Interview kits) |
| NOTION_OPEN_ROLES_DB | Your roles database id in Notion |
| NOTION_OPEN_ROLES_DATA_SOURCE | Its data source id (`collection://<THIS>`) |
| NOTION_OB_TEMPLATE | Your Opportunity Brief template page id |
| NOTION_GOLD_OB_EXAMPLE | A finished OB you consider gold standard |
| NOTION_EXAMPLE_ROLE_PAGE | A role page showing your per-role tracker layout |
| NOTION_IK_SOP | Your interview-kit SOP page id |
| NOTION_ATOMIC_JD_PROMPT | Your JD style-guide page id |
| NOTION_JD_BASELINES | Your internal conversion-baselines page id |

Secrets are NOT tokens: the Teamtailor API key goes in `~/.claude/settings.json` under
`env.TEAMTAILOR_API_KEY`, and your recruiter email under `env.ATOMIC_RECRUITER_EMAIL`.
