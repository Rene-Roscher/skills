# Claim labels and citations

Load when you write a plan, report or review that others will act on, or when you act on a subagent's report.

## Labels

| Label | Meaning | Example |
|---|---|---|
| verified | You opened the source or ran the check in this session | "The bookings table has no `cancelled_at` column (verified: `db/schema.sql:42`)" |
| reported | Someone or something else said it and you did not re-check: a subagent, a tool summary, a doc, a ticket, the user | "The payment provider retries webhooks for three days (reported: research note, not re-checked)" |
| inferred | Reasoned from verified facts | "So cancelling needs a migration (inferred from the line above)" |

A claim that no source confirmed is not labeled; it is marked unverified, with the check in the same
sentence: "Unverified: the client may enable RESP3 by default. Check: the client's changelog for the locked
version."

A project may use its own words for the labels (for example German labels in internal documents). Keep the
three meanings and the unverified marker.

## Before a reported claim carries a decision

1. Find the claim that the decision rests on. Usually one or two claims carry the whole plan.
2. Open the thing it is about: the file and line, the endpoint, the command output, the vendor page.
3. If it holds, relabel it verified with the source. If not, say what you found instead and change the plan.
4. Two reports that contradict each other always trigger this check, even when the decision seems small.

Typical failures of unchecked reports:

- A JSON query tool returns `null` for a missing key, and the report reads that as "the field is nullable".
- Limits are checked one by one and never summed against the total.
- A proposed security fix was never tried against legitimate traffic.
- Assumptions about the project's own code were never compared with the code.

## Numbers

- Recount from raw data instead of copying a number from a report.
- Check sums against totals and parts against the whole.
- Say the unit and the population: "12 of 40 endpoints", not "30 %".
- An implausible number is a tool error until shown otherwise.

## Citation format

- External fact: `(source: [URL], version [x], retrieved YYYY-MM-DD)`.
- Code fact: `path:line`, or `path:line-line` for a range.
- Command output: the command and the lines that matter.
- Facts that will change with versions go into an "Old patterns" section with the version range they apply to,
  instead of wording such as "before the update" or "since last year".

Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (old patterns,
verified 2026-10).

## Example: a short plan with labels

```markdown
## Evidence
| Claim | Label | Source |
|---|---|---|
| Invoices have no `voided_at` column | verified | db/schema.sql:88 |
| The PDF library supports watermarks in the locked version | verified | vendor docs for 3.2, retrieved 2026-10-31 |
| Customers want a void reason | reported | support ticket summary, not re-checked |
| Voiding needs a migration | inferred | from the first row |
```
