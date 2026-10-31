# Completion report

Load when you are about to report completion.

## Status ladder

| Status | Meaning |
|---|---|
| implemented | The code is written |
| tested | Automated tests pass |
| verified | You watched the behaviour in a running system |
| deployed | The release run succeeded |
| live | You saw the change at the production surface |

Done needs verified; a release task needs live. The project maps these to its tracker, for example tested and
verified to a review state with a needs-verification label, and live to done.

## Template

```markdown
## Completion report

| # | Item (as requested) | Status | Evidence |
|---|---|---|---|
| 1 | [item text, verbatim] | verified | [what you ran or saw, with output or a screenshot path] |
| 2 | [item text, verbatim] | tested, not verified | [test run]; not verified because [reason] |

Runtime gate: [one line per running component, or "not applicable"]
Environment differences checked: [list, or "none apply" with the reason]
Failing checks: [name and output lines, or "none"]
Next step to verify: [what someone has to do, for items that are not verified]
```

## Example (invoicing app)

```markdown
| # | Item (as requested) | Status | Evidence |
|---|---|---|---|
| 1 | Fix the rounding of the VAT line on credit notes | verified | Rendered a credit note for 3 x 9.99 at 19 % in the dev app; the VAT line shows 5.69. Regression test fails without the fix (expected 5.69, got 5.70) and passes with it |
| 2 | Send the credit note by mail | tested, not verified | Mail test passes with a fake; the template was not rendered for real because the dev mail catcher is down |
| 3 | Release it today | merged, deploy not confirmed | The deploy run has not started; no production check possible |
```

Do not write "all done" under a table like this. Name the items that are done and the ones that are not.
