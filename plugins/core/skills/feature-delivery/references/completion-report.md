# Completion report

The owner reads it to decide what happens next, so it gives status, evidence and decisions, and links to files,
tests and the pull request for detail. A length limit, if the project wants one, lives in its profile.

## Template

```text
Plan: [path], approved by [name]

Steps
| Step (verbatim from the plan) | Status | Evidence |
|---|---|---|
| 1. ... | verified | [how it was seen working] |
| 2. ... | tested, not verified | [test names]; not verified because [reason] |
| Extra point from the user: ... | implemented | [what is missing] |

Tests and checks
- [command]: [result, for example 212 passed, 1 failed]
- Failing: [test name] - [first lines of the output]. [Related or unrelated, with the evidence: fails on the base
  commit too, or not checked]

Definition of done
- Rejected: [item] - [reason]
- Deferred: [item] - [issue link], [priority]

Deviations
- [entry from the plan's deviation log, or "none"]

Open
- [what remains, with issue links]

Needs a decision
- [question, options, recommendation, or "none"]
```

## Rules for the content

- One status per item, from the ladder: implemented, tested, verified, deployed, live. "Done" is not a status.
- Name every failing test or check with its output, including ones you believe are unrelated.
- "Unrelated" needs evidence. Without it, write "not checked whether related".
- Do not write "all tests pass" unless the full suite ran and passed in this session.
- Report what was not verified as plainly as what was.
