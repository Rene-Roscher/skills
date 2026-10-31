# Deviation rule

## Small or assumption-breaking

Ask one question: did the owner rely on this when approving the plan? If yes, it is an assumption break, and the
work stops until the owner answers. If no, log it and continue.

| Found during the build | Kind | Why |
|---|---|---|
| A service is named `InvoiceSender` in the code, the plan says `SendInvoice` | small | naming only |
| A helper class is needed that the step table does not list | small | no new behaviour |
| The plan names a file that has since moved | small | layout only |
| A migration needs an extra index the plan did not list | small | additive, covered by the plan's query list |
| The plan assumes integer cents in `amount_cents`; the table stores a decimal `amount` | breaks money | rounding and every calculation depend on it |
| A booking system's plan assumes one booking per slot; the schema allows several | breaks data model | uniqueness, conflicts and the UI states change |
| The plan says members may export; the permission model has no export permission | breaks permissions | someone has to decide who may do it |
| The change would touch every tenant at once (shared config, global cache key, scheduler) | breaks blast radius | the approved scope was one feature |
| A third-party API field the plan relies on is deprecated or missing | breaks external contract | the integration design changes |
| A step needs a destructive migration or deletes data | breaks irreversibility | no rollback |
| A required step is impossible as written and needs a different approach | breaks the plan | the owner approved that approach |

When unsure, treat it as an assumption break. A short question costs less than rework on an unapproved design.

## Log entry for a small deviation

Add it to the plan's `Deviations` section when it happens, not at the end:

```text
- Step 3: helper `TaskCsvRow` added to keep the export controller thin. No behaviour change.
- Step 5: index on (project_id, created_at) instead of (created_at); every export query filters by project first.
```

## Asking about an assumption break

Stop work on the affected steps. Steps that do not depend on the assumption may continue only if you say so in
the question. Ask with:

```text
Plan assumption: [quote from the plan, with section]
What the code shows: [fact, with path:line or command output]
If we proceed as planned: [what breaks or changes]
Options:
  A) [option] - consequence
  B) [option] - consequence
Recommendation: [A or B, one reason]
Paused: [steps on hold]   Continuing: [steps unaffected, or "none"]
```

After the answer, record the decision in the plan's deviation log with who decided and when, then continue.

## Not a deviation

- Fixing a typo in the plan.
- Choosing between two equivalent internal implementations that the plan left open.
- Adding a test the plan did not list.
