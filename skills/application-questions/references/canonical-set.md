# The 6 canonical ✪ application questions

Reused across every role **by id, never rewritten**. Icon **✪**, tags `application` + `canonical`, each mapped to a scorecard dimension. Title = the short spoken question; the detail lives in the description (a long title breaks the web form). You attach these; you do not author or edit them.

| # | id | field | scorecard dim | mandatory on the job? | spoken title |
|---|----|-------|---------------|-----------------------|--------------|
| 1 | **75227** | Text | Logistics 67341 | ✅ mandatory | "Where are you based? (City & Country)" |
| 2 | **34786** | Range 0-10 | Communication 23515 | ✅ mandatory | "How's your English for work?" |
| 3 | **35702** | Text | Logistics 67341 | ✅ mandatory | "What compensation are you looking for?" |
| 4 | **212587** | Text | Logistics 67341 | ✅ mandatory | "What availability are you looking for?" |
| 5 | **58122** | Text | Motivation 67336 | optional | "What drew you to this role?" |
| 6 | **212588** | Text | Core skills 67334 | optional | "Do you have work you could share?" |

- **Mandatory:** English, location, salary, availability, **and the role reality-check(s)** you author.
- **Optional:** interest (58122), show-your-work (212588). Optional is set as `mandatory:false` on the **job's picked_question**, not on the bank question.
- **Salary framing** = agency framing: learn THEIR preferences to match them, not to gate against a band.
- The old "anything else" question **#35145** was merged into interest (58122) and should be archived — do not pick it.

These six are already attached to the golden template job (659646 "Atomic Template"), so a job cloned from the template inherits them. When building a job that did NOT come from the template, attach all six by id with the flags above, then add the role's ⌖.

## Icons
- **✪** = canonical baseline (these six).
- **⌖** = role-specific reality-check (authored per role — see `role-questions.md`).

(Interview-kit icons are different: ★ canonical, ✳️ optional, 🧩 role-specific. Don't cross the two vocabularies.)
