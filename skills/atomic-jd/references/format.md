# Atomic-JD format + anonymization

The house structure for a public posting, from the "Atomic JD" prompt (Notion Document Hub id `366a97e2-3bc3-8052-b243-f1a8a453b4a9`). Omit a section when there is no data for it. Do not invent metrics or names.

## Structure

Two house elements bookend the content and are easy to forget: a **Top Bar** as the very first line (`[Department] · [Location or Multiple locations] · [Remote status]`, e.g. `Product · LATAM · Fully Remote`), and an **Apply CTA** (`Apply for this job`) right after the hook. Include both. The numbered content sections:

1. **Title line** (this becomes the poster `title`) — use the structure that performs on Teamtailor:

   ```
   [Role] ([specialty / stack]) | [company context] | Remote ([geo]) [1–2 emoji]
   ```

   Example: `UX Designer (Product Workflows) | US B2B SaaS | Remote (LATAM) 🎨`.

   Backed by the live job data (45 jobs, avg applications by title feature):
   - **Always include "Remote" and the geo.** Titles with "Remote" average 176 applications vs 76 without (2.3×); with a named geo (LATAM/US/Americas) 183 vs 126. This is the biggest lever, never drop it.
   - **Pipe-separated segments** (176 vs 115). Use `|`.
   - **Role first**, with the specialty or stack in parens, because that is what candidates search: `(React Native + Swift/Kotlin)`, `(Meta)`, `(Product Workflows)`, `(Product Ops)`. The parens are also where the craft lives, so the title stays candidate-first.
   - **Use the accurate, commonly-searched role name as the anchor — this drives conversion, not just views.** A mislabeled title pulls the wrong audience, who view and bounce. In the data, two near-identical JDs for the same Account Manager role converted 13.6% vs ~5% purely because one title said "Marketing Account Manager" (accurate) and the other said "Client Success Manager" (wrong audience). The title filters *who* sees the post, so an honest, specific role name lifts both reach and conversion. Do not get clever with the role name.
   - **Concrete context beats a generic label.** "Performance Marketing for Universities 🎓", "AI-powered SEO 🚀", "Live SaaS app 📱" out-pull "US B2B SaaS". Say something real about the client (still anonymized) in the context slot.
   - **Company context** as a middle segment, anonymized: "US SaaS startup", "ECommerce", "Marketing Agency", "US B2B SaaS".
   - **1–2 on-brand emojis** (🚀 🐍 💻 📊 🎨 🧭 📱), mild positive effect. No pile-ups, none in bullets.
   - Seniority words do not lift volume on their own (confounded by smaller senior pools); include seniority only when it is a real filter for the role.

2. **Hook** (this becomes the poster `pitch`, ≤ 200 characters)
   One or two sentences, specific to what the person will actually own and why it matters. No promotional adjectives.

3. **Company Overview** (short paragraph, anonymized)
   Open with "Our client is a …". Use only the metrics the brief provides.

4. **Your Role** (short paragraph, then the bullets below)
   Why the role exists and what success looks like. **Both must come from the brief's own "About the Role" and "Success Indicators" text — never invent a backstory or motivation.** Do not write things like "the flows got tangled and nobody owns them" or "fast teams build the wrong thing twice" unless the brief actually says so; that is fabricating the why. If the brief does not explain why the role exists, describe the role plainly and drop the why. This paragraph is also where cohesion lives: it should set up the "You'll" bullets, so the whole post reads as one story rather than disconnected sections.

5. **You'll** (5–8 bullets)
   Each starts with a strong verb, 5–14 words, concrete to the domain and seniority.

6. **You Bring** (5–8 bullets)
   Hard skills, judgment, and communication. Include English/communication when relevant.

7. **Bonus Points** (3–6 bullets, optional)
   Only real add-ons implied by the domain or stated in the brief.

8. **What's Offered** (4–7 bullets)
   Remote/flex, compensation, PTO, team shape, and the concrete upside.
   **Compensation framing (important, privacy).** Present pay as *Atomic's own market estimate for a role like this*, never as the client's band. The client's real budget is private, and a client-attributed number lets competitors outbid them. Write it as guidance to the candidate and invite their range: "What we'd estimate for a role like this: around $X to $Y USD/month, based on experience, paid weekly in USD as a contractor. Share the range that fits your level and we'll go from there." Quote it monthly in USD for LATAM contractors (convert an hourly brief figure: hours/week × 4.33), and keep it a range tied to experience. If the brief gives no number, write "Compensation based on experience; share your target range" and never invent one.

9. **Interview Process** (3–5 numbered emoji steps) — **only from real data, never invented.**
   Use the process the brief or OB actually states, or the role's real Teamtailor pipeline. If the brief does not give one, **omit the whole section** rather than making up stages. Do not soften or embellish real stage names ("Final conversation with the CEO" is fine only if that is the real last step). Format as `1️⃣ 2️⃣ 3️⃣`, each summarized in 5–10 words.

10. **About Atomic HR footer — do NOT add it.** The career site appends this block to every posting automatically, so including it in the body duplicates it. End the body at the Interview Process (or the last real content section). Only add an About-Atomic paragraph if the user explicitly asks for a standalone JD that will live somewhere the site footer does not reach.

## Body that converts (from the win/loss data)
Conversion (applications ÷ page views) is the reliable quality signal: it reproduces within ~1 point across reposts of the same JD, while views swing with reach and freshness. Optimize the body to beat the client-and-family conversion baseline in `benchmarks.md`. What separated high- from low-converting JDs on the *same role and client*:

- **Give the role a shape in five seconds — but never invent numbers.** Only show proportions ("Creative 33% / Ads 33% / Client 33%") if the brief actually states them. A made-up "~40%" is fake precision and reads as AI-generated; do not do it. When you do not have real proportions, either group the work under plain focus-area headers, or just use one tight bulleted list (the top-converting eng JD used five plain bullets, no groups, no percentages). Grouping is optional. What loses is the long, flat, undifferentiated dump: a 12-bullet "Your Role" list converted 5.3% against 12.2% for the same role written tighter.
- **Tight, grouped bullets, ~5 per section.** High converters average ~19 bullets total; low converters ~26. Cut and group rather than list everything.
- **An opinionated, self-selecting voice.** State plainly what the role is and is not, and the 3–4 traits that actually matter ("This is not a make-briefs-and-wait role. You connect performance signals to creative without being told to."). Filtering the wrong people out raises conversion, because the right people are who is left reading. This is precision, not promotion, so it still obeys the voice rules.
- **Concrete team context.** Team size, who you report to, who you work with, how decisions get made. Access and specificity convert (the top eng JD sold "the second engineer on a two-person team, in decisions alongside the CEO").
- **A real, concrete offer.** Actual perks (PTO specifics, equipment, direct access to leadership) plus a salary number beat "competitive compensation". Label bonus/nice-to-haves as genuinely optional, so qualified-but-unsure people still apply.
- **A real interview process, or none.** Include it only with real specifics (stages, durations, who runs each); never invent it.

## For Teamtailor specifically
- `title` = the Title line (section 1), emojis included.
- `pitch` = the Hook (section 2), ≤ 200 characters.
- `body_html` = sections 3 through 10 as HTML: `<p><strong>Header</strong></p>` for section headers, `<ul><li>` for bullets, `<br>` between numbered interview steps. The title/hook live in TT's own title/pitch fields, so the body starts at "Your Role" or "Company Overview".
- `internal_name` = `Role (Client)` — internal only, may name the client.

## Anonymization — how to generalize without going generic
Keep it truthful and specific on everything except identity. The house pattern (from a live anonymized posting):

> Our client is a profitable, bootstrapped U.S. B2B SaaS company that has been in market for over ten years, serving property managers and field teams. [...] Scale so far is tens of thousands of active users and over 100 million inspection photos, run by a team of around 20 with roughly half in engineering and product.

- **Drop:** the company name, product names, named integrations/partners, and any unique identifier or link that reveals who it is.
- **Keep:** years in market, user counts, volumes, team size, funding posture (bootstrapped/profitable), the vertical, and the real nature of the work.
- **Generalize named things:** "integrates with the major property-management platforms" (not the vendors); "a recent AI feature that turns spoken notes into structured reports" (not the product's brand name).
- **Title context slot:** a generic industry label ("Property Inspection SaaS", "US PropTech SaaS"), never the client name.
