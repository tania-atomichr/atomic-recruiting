# Generating TT share links via the browser

Share links (and thus interview transcripts) can't be created through the TT public API — they're a
UI action. Drive the recruiter's logged-in Teamtailor via the **claude-in-chrome MCP**, using the
**javascript_tool** (`mcp__claude-in-chrome__javascript_tool`). Coordinate/element clicks are flaky
on this React SPA; JS is reliable.

## Why share-by-EMAIL (not share-by-link)
The "Generate share link" button creates a share but **does not surface the URL** to automation. So
instead use **Share by email** to **the recruiter's OWN inbox** and read the link back from their own
Gmail. This also matches the recruiter's own habit.

**RECIPIENT = the current user's own inbox, never a hardcoded person.** Resolve it, in order:
1. the env var `ATOMIC_RECRUITER_EMAIL` (set during setup: `echo $ATOMIC_RECRUITER_EMAIL`),
2. else the address of the connected Gmail account (`get_profile` / the account they authorized),
3. else ask the user "which inbox should I send the share to?" once.
Every JS snippet below reads a `RECIPIENT` const at the top; fill it with the resolved address. Never
send another teammate's shares to someone else's inbox.

## Open the share dialog directly by URL
Navigate the MCP tab straight to the modal (saves clicking the share button):
```
https://app.teamtailor.com/companies/{{TT_COMPANY_ID}}@na/jobs/<JOB_ID>/stages/candidate/<CID>?modal=%7B%22component%22%3A%22share-link%22%2C%22arg%22%3A%7B%22candidateId%22%3A%22<CID>%22%7D%7D
```
(That `modal=` param is URL-encoded `{"component":"share-link","arg":{"candidateId":"<CID>"}}`.)

## Recipe A — full share WITH meeting recordings (Phase 4: to get transcripts)
Meeting recordings are checked by default, so just switch to the email tab, fill the recipient, send.
Run this as ONE javascript_tool call per candidate (after navigating to the modal URL). Set `RECIPIENT` to the resolved own-inbox address before running:
```js
const RECIPIENT='<your-own-inbox>';  // ATOMIC_RECRUITER_EMAIL / connected Gmail account, never hardcoded
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let tab;for(let i=0;i<25;i++){tab=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='Share by email');if(tab)break;await sleep(300);}
if(!tab)throw'notab'; tab.click(); await sleep(800);
// find the email textarea via its "Email addresses" label (placeholder is empty, so match the label)
const lblEl=[...document.querySelectorAll('*')].find(e=>e.childElementCount===0&&e.textContent.trim()==='Email addresses');
let f=null,sc=lblEl;for(let i=0;i<4&&sc&&!f;i++){sc=sc.parentElement;if(sc)f=sc.querySelector('textarea');}
const set=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
set.call(f,RECIPIENT); f.dispatchEvent(new Event('input',{bubbles:true})); f.dispatchEvent(new Event('change',{bubbles:true}));
await sleep(400);
const b=[...document.querySelectorAll('button')].find(x=>/send email/i.test(x.textContent)&&!x.disabled); // its text is "Send email Send email"
'DONE:'+(b?(b.click(),'SENT'):'no-btn')
```

## Recipe B — CLIENT-SAFE share (Phase 7: contact + résumé + summary only)
Keep only **Personal information, Resume, Resume summary**; uncheck everything else (LinkedIn, Pitch,
Locations, Answers, References, and every per-job section — which drops meeting recordings, Q&A,
internal docs). Two hard-won rules:
1. **Uncheck SYNCHRONOUSLY** — a loop with `await sleep()` between checkbox clicks **freezes the
   renderer** (CDP timeouts). Click them in a tight synchronous `forEach`, no awaits. Clicking a
   job-section header checkbox cascades its children off, so 2-3 passes clears ~40 checkboxes fast.
2. **Gate the send** on exactly the 3 intended fields, so a partial uncheck never leaks data.
```js
const RECIPIENT='<your-own-inbox>';  // ATOMIC_RECRUITER_EMAIL / connected Gmail account, never hardcoded
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const KEEP=new Set(["Personal information","Resume","Resume summary"]);
function lbl(cb){let n=cb.closest('label')||cb.parentElement;for(let i=0;i<4&&n;i++){let t=(n.textContent||'').trim();if(t&&t.length<50)return t;n=n.parentElement;}return '?';}
let tab;for(let i=0;i<25;i++){tab=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='Share by email');if(tab)break;await sleep(300);}
if(!tab)throw'notab'; tab.click(); await sleep(800);
for(let p=0;p<3;p++){[...document.querySelectorAll('input[type=checkbox]')].forEach(cb=>{if(cb.checked&&!KEEP.has(lbl(cb))){try{cb.click()}catch(e){}}});} // SYNC, no await
await sleep(300);
const lblEl=[...document.querySelectorAll('*')].find(e=>e.childElementCount===0&&e.textContent.trim()==='Email addresses');
let f=null,sc=lblEl;for(let i=0;i<4&&sc&&!f;i++){sc=sc.parentElement;if(sc)f=sc.querySelector('textarea');}
const set=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
set.call(f,RECIPIENT); f.dispatchEvent(new Event('input',{bubbles:true})); f.dispatchEvent(new Event('change',{bubbles:true}));
await sleep(400);
const kept=[...document.querySelectorAll('input[type=checkbox]')].filter(c=>c.checked).map(c=>lbl(c));
let res='SKIP-wrong-count:'+kept.length;
if(kept.length===3&&kept.every(k=>KEEP.has(k))){const b=[...document.querySelectorAll('button')].find(x=>/send email/i.test(x.textContent)&&!x.disabled);res=b?(b.click(),'SENT'):'no-btn';}
JSON.stringify({kept,res})
```
Per candidate: one `navigate` + one javascript_tool call. Expect `{"kept":["Personal information","Resume","Resume summary"],"res":"SENT"}`.

## Retrieving the links from Gmail (Phases 4 & 7)
The share emails are large HTML; reading 10+ in the main context is wasteful. **Spawn a subagent** to
do it. Give it the candidate names + ids and have it:
- Load Gmail tools via ToolSearch (`select:mcp__<gmail>__search_threads,...get_thread`).
- `search_threads` for `to:<RECIPIENT> newer_than:1h subject:review` (RECIPIENT = the user's own inbox; sort newest).
- For each candidate pick the **newest** matching thread (there may be an older full-share email too),
  `get_thread` FULL_CONTENT, and pull the `https://tt.na.teamtailor.com/shares/<TOKEN>/<CID>` line from
  `plaintextBody`. `MINIMAL`/`METADATA` formats omit the body — must be FULL_CONTENT.
- Return ONLY `{cid: url}` and verify each URL ends with the right cid.

## Fetching a transcript + CV from a share page (no auth)
```python
import requests,re,html
t=html.unescape(re.sub("<[^>]+>"," ",requests.get(url,timeout=60,headers={"User-Agent":"Mozilla/5.0"}).text))
# The page contains a "Transcript" section (speaker-by-speaker) and the "Résumé/Experience" text inline.
```

## Environment notes
- List the browser first: `mcp__claude-in-chrome__list_connected_browsers`. If none, ask the user to
  connect their Chrome; don't fall back to desktop control.
- Verify each send via the API activity feed (`code=="share"`, recent) rather than trusting the UI.
