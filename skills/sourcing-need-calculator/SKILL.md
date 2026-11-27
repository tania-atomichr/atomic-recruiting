---
name: sourcing-need-calculator
description: Explain or check how many more people a search needs, using the sourcing app's own funnel math (six stages, conversion rates multiplied backwards from the open seats). Use when someone asks why a search says "Add ~N", "Reach out to N" or "Covered", how many profiles a new search will take, whether a search is over-sourced, or wants a number checked by hand. The app computes the live answer; this skill explains it and never replaces it.
---

# Sourcing need calculator

How the sourcing app decides, for every open search, whether it needs more people and how many. The math lives in the sourcing app (`sourcing_plan.py`, read through `GET /sourcing-need` and the Searches page). This skill is the written-out version of that code, so anyone can explain a number or check one by hand.

## One calculator

The app is the only place the live number is worked out. The Searches row, its button, the completeness bar, the Why pop-up, the client portal's sourcing column, the invite order and the scorer all read that one answer.

- For a live search: read the app's answer (Searches page, or `GET /sourcing-need`) and explain it with the rules below. Never work out a different number and present it as the search's need.
- For a search that does not exist yet, or a "what if": use the math below with the team rates, and say it is an estimate (write "~").
- If your hand calculation and the app disagree, that is a finding to report with both numbers, not a number to replace.

## The six stages

Every screen uses the same six stages, in this order:

| Stage | Who is in it |
|---|---|
| To reach out | Added to the search, not reached out to yet, scored, nothing flagged ("ready") |
| Reached out | Reached out to in the last 14 days, no screening yet, has not said no |
| Booked | A screening booked (in the app, or the person is at a screening or later on the search's own Teamtailor job), not yet with the client |
| Client | Shown to the client and waiting for an answer, or in the client's own interviews |
| Offer | An offer out |
| Hired | Hired on this search |

One person, one stage: each person counts once, at the furthest stage they reached.

## The rates (what usually happens)

Each step between two stages has a ratio: how many people at the lower stage it takes to get one at the next. Only multiplication is used.

| Step | Ratio | Where it comes from |
|---|---|---|
| Hired from Offer | 1 / 0.84 = 1.19 offers per hire | Our offers: 27 of 32 that ended became a hire |
| Offer from Client | 0.84 x people shown per hire = 5.04 (9 x 0.84 = 7.56 on senior searches) | Our filled searches: about 6 people shown per hire, about 9 on senior and lead searches |
| Client from Booked | 1 / share of bookings that reach the client (team default 32%, so 3.12) | Bookings made 21 days ago or more, so they have been decided |
| Booked from Reached out | 1 / booking rate (team default 8%, so 12.5) | People reached out to 7 days ago or more, so they have had time to answer |
| Reached out from To reach out | 1 | Every person reached out to is first a profile added |

How the rates are chosen:

- **Plan from reached out, not from added.** Added-to-contacted is not a conversion; it mostly counts people added after a search already had enough.
- **Team rate first, the search's own later.** A search uses its own booking rate once 30 people were reached out to on it 7 or more days ago, and its own share-to-client once 10 of its bookings are 21 or more days old. Until then it uses the team's rate and says so.
- **The team rate itself** is read live from everyone ever reached out to (needs 100 mature people, else the 8% default) and every decided booking (needs 30, else the 32% default). So the live ratios move a little from the defaults above.
- **Floors** keep the math from dividing by zero: a search's own booking rate never goes below 1%, its share-to-client never below 5%.
- **Senior** means the search title contains senior, sr, lead, head, principal, staff, director, vp, chief, controller or founding.
- Ratios are kept as a person reads them: two decimals under 10 (3.12), one decimal from 10 to 20 (12.5), whole from 20 up.

## The math, stage by stage

Start at the open seats and work backwards. At each stage: what is needed there, minus the people already there, times the ratio to the stage before.

```
Offer needed     = open seats x 1.19                     minus offers out           = Offer missing
Client needed    = Offer missing x 5.04                  minus what Client holds    = Client missing
Booked needed    = Client missing x 3.12                 minus people booked        = Booked missing
Reached needed   = Booked missing x 12.5  (whole people) minus people reached out   = Reached out missing
Add              = Reached out missing                   minus people ready to reach out
```

What Client holds: each person waiting for the client's answer counts 1; each person in client interviews counts for more, 1.5 on a regular search (0.25 of a hire x 6 shown per hire, never less than 1) and 2.25 on a senior one.

**From zero** is the same chain with nobody in play. It is the "out of" for the completeness bar and the first sentence of the Why: "From zero, 1 hire on a typical search takes ~N profiles."

### Rounding

- Fractions stay inside the math. Every stage is a fraction of a hire.
- **Under half a person short is enough.** At Client and at Booked only, a gap smaller than 0.5 of a person is let go and the Why says "under half a person: enough". Offers are never rounded: 1.19 offers per hire is the chance an offer falls through, not a head count.
- Reached out needed is rounded to whole people. Rounding up at every stage was tried on the live searches and not taken: the stages multiply, so it nearly doubled the profiles asked for.
- A stage with enough covers every stage after it: what the later stages still miss is expected from the people already in play.

## Who counts for nobody

These rules keep the numbers from being too positive:

- **Rejected or dropped = 0**, at once, in any stage, whether the app or Teamtailor shows it.
- **Silent 14 days = 0.** A person reached out to more than 14 days ago with no screening does not count in Reached out. A person whose screening was 14 or more days ago and was not moved on does not count in Booked (they are named so someone moves them on or rejects them). A person shown to the client with no answer in 14 days counts as passed.
- **A draft in the client portal that was never sent counts for nobody.** Account managers use drafts to compare candidates.
- **Not ready = not counted in To reach out.** People added but not scored yet, or flagged for review, are shown beside the number and not counted.
- **Applicants** count only once they reached a screening on the search's own job in the last 14 days, and not if rejected, hired, or already counted with the client.
- **Two cards for one person** (for example a LinkedIn card and an email card) count once.

## Teamtailor and the client portal: the newer record wins

- A screening Teamtailor shows on the search's own job is a booking, even if the card in the app was never moved.
- A person Teamtailor shows at one of the client's own steps (interview, test, task, final round, offer) counts with the client, unless rejected there, or the client portal shows them out, or the client portal already counts them. "Submit to client" and "Submitted" are not client steps: sending happens in the client portal.
- When the search is linked to the client portal and the portal has answered, the portal decides who is alive with the client; a card left in a client column in the app after a no does not count.
- Hired: the larger of the app's and the portal's count, never the sum.

## What the answer says (the step)

The first true of these, in order:

| Step | When | What happens |
|---|---|---|
| On hold | The search or its client is paused, or someone put it on hold | Nobody new: no reads, no scoring, no outreach |
| Filled | Every seat is hired | No new people |
| Offer out | Offers cover every open seat and nothing more is needed | No new people unless an offer falls through |
| Covered | The people in play cover the need (Add and Reach out are 0) | Keep working the people in play; add nobody |
| Reach out to N of the M ready | The people already added cover the gap | Reach out to them; add nobody new |
| Add ~N | More people are needed even after the ready ones | Add about N more |

The priority is the step: Add is high, Reach out is medium, Covered, Offer out and Filled are low. A search cannot be high priority and covered at once.

A search is **over-sourced** when the ready pile is at least 20 more than needed and at least twice the need.

## What the answer drives

- **Invites.** The day's invites go first to searches that still need people, shared by need (a search that needs 200 gets four places for each one a search that needs 50 gets), best fit first. People beyond the needed number wait as the reserve. On Covered, Offer out and Filled searches the app sends no new invites; they start again by themselves when the search needs people. Replies, follow-ups and invites a sourcer presses by hand still go. No cap changes.
- **Scoring.** The scorer waits on a search that has enough (Reach out, Covered, Offer out, Filled) and on closed or paused searches, and takes only the N newest unscored people on a search that says Add ~N. The add screens say so before people are added.
- **Hidden searches.** An admin can hide a search (or every search of a client) from sourcers. Only admins and the people put on it see it; nobody else can add people or start outreach on it.
- **The completeness bar** is 1 minus Reached out missing divided by the from-zero number. It shows 100 only when the step is Covered, Offer out or Filled, and goes down by itself when people drop out.

## Worked example

A regular (not senior) search, 1 open seat, team rates (8% book, 32% reach the client), on the default ratios: 1.19, 5.04, 3.12, 12.5.

In play: 1 person waiting for the client's answer, 1 in client interviews, 3 booked, 10 reached out in the last 14 days, 20 ready to reach out.

**From zero:**

```
1 hire x 1.19        = 1.19 offers
1.19 offers x 5.04   = 6 people with the client
6 x 3.12             = 18.7 booked
18.7 x 12.5          = 234 reached out
234 x 1              = 234 profiles
```

So 1 hire on a typical search takes ~234 profiles.

**With the people in play:**

```
Offer      need 1.19   have 0                               missing 1.19
Client     need 1.19 x 5.04 = 6     have 1 + 1.5 = 2.5      missing 3.5
Booked     need 3.5 x 3.12 = 10.9   have 3                  missing 7.9
Reached    need 7.9 x 12.5 = 99     have 10                 missing 89
To reach   need 89                  have 20 ready           add 69
```

The row says **Add ~69**. The Why opens: "From zero, 1 hire on a typical search takes ~234 profiles. The people already in play leave ~89 to reach out, 20 are ready to reach out, so add ~69." The completeness bar reads 1 - 89/234 = 61%.

**When it turns Covered:** with 2 waiting on the client, 1 in interviews and 8 booked, Client holds 3.5, so 2.5 more are needed at Client, which takes 2.5 x 3.12 = 7.8 booked. 8 booked is more than 7.8, so Booked has enough, nobody more needs reaching out, and the row says **Covered**, whatever the size of the ready pile.

**Half a person:** if Booked needed were 8.3 with 8 booked, the gap of 0.3 is under half a person, so Booked has enough and the Why says so.

## Checking a number someone doubts

1. Read the app's answer for the search (the Searches row and its Why).
2. Read the people behind each stage in the app, and compare with the search's Teamtailor job and the client portal.
3. Redo the chain above with the rates the Why shows. Every line must multiply to the next one and end on the button's number.
4. Report names, not only counts, and say which rule left each person out (rejected, 14 days silent, draft, not ready, counted once).
