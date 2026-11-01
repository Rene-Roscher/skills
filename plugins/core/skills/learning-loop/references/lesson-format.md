# Lesson format

Load when writing or reviewing a lesson or an index line.

## Contents

- Template
- Index line
- Examples
- Good and weak lessons
- Checklist

## Template

```markdown
---
name: formatter-own-files-only
description: Run a formatter or fixer only on the files you changed, passed by name, never on a directory
type: feedback
---

Run the formatter only on the files you changed, passed by name.

**Why:** Formatting a whole directory rewrote two files that someone else was editing, and their work ended
up in this change. (2026-10-04)

**How to apply:** Before any formatter or fixer run (prettier, black, gofmt -w, php-cs-fixer), build the file
list from `git status --porcelain`, limited to files you changed. After the run, check `git status` again; a
file you did not touch means stop and read its diff before anything else.

Related: [[commit-only-own-changes]]
```

- `name` equals the file name without `.md`, lowercase with hyphens.
- `description` is one line that says when the lesson applies. It is what you match against before acting.
- `type`: `feedback` (behaviour), `project` (a dated decision or ongoing work), `reference` (where to find
  something), `user` (a personal preference). Auto memory may nest it as `metadata: type: ...`; both forms are
  fine.
- The Why is the incident, abstracted: what was done, what broke, how it showed. Add the date.
- The How to apply names the trigger (a file pattern, a tool, a command, a moment such as "before a release")
  and the check. If you cannot name a trigger, it is not a lesson yet.
- Links: `[[name]]` or a relative Markdown link to related lessons, and to the fact or artifact it relies on.

## Index line

```markdown
- [Formatter on own files only](formatter-own-files-only.md): any formatter or fixer run
```

One line, under about 150 characters. Title plus trigger. No Why, no history.

## Examples

A project lesson with a date and an end condition:

```markdown
---
name: refund-export-paused
description: Refund CSV export is switched off until the tax-rounding fix ships; do not re-enable it
type: project
---

The refund export stays off until the rounding fix for partial refunds is released. (decided 2026-10-20)

**Why:** The export rounded each line instead of the total, so totals differed from invoices by a few cents.

**How to apply:** Do not touch the `refund_export` feature flag. When the rounding fix is released, delete this
lesson and its index line.
```

A promoted lesson after the artifact exists:

```markdown
---
name: money-integer-cents
description: Money is stored and computed as integer cents in invoices, payments and credits
type: feedback
---

Money is integer cents. Enforced by `tests/Architecture/MoneyColumnsTest`.

**Why:** Twice a migration added an amount as a float column; sums drifted by a cent on large invoices.

**How to apply:** Any new amount column or field. If the architecture test fails, fix the column type, never
the test.
```

A reference lesson:

```markdown
---
name: where-booking-secrets-live
description: Where the booking system's credentials are managed, for any task that needs one
type: reference
---

Credentials for the booking system live in the team secret manager under the project's folder; local
development reads them from `.env`, which is never committed. Ask for access instead of asking for the value.
```

## Good and weak lessons

| Weak | Better |
|---|---|
| Be careful with the formatter. | Run the formatter only on files you changed, passed by name. |
| Dates are tricky. | Booking times are stored in UTC and converted with the venue's time zone at the edge; a test that compares local strings must pin the zone. |
| The API key is `...` | The API key is in the secret manager under the project folder. |
| Use port 5433 for the test database. | Fact, not lesson: put it in `docs/PROJECT-FACTS.md`. |
| Never use floats. | Money is integer cents (with the incident and the test that enforces it). |

## Checklist

- [ ] No secret, credential, personal data or customer name.
- [ ] Searched the store; no existing lesson covers this.
- [ ] Rule in one or two sentences, as an instruction.
- [ ] Why with the incident and date.
- [ ] How to apply with a trigger and a check.
- [ ] Links to related lessons and to the fact or artifact.
- [ ] One index line added or updated.
- [ ] `check_lessons.py` clean.
