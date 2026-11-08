# Executor spec template

## Contents

- How to use it
- The template: header, Goal, Scope, Out of scope, Files, Protected files, Context, Steps, Acceptance,
  Stop and ask, Report, Executor rules

## How to use it

Copy everything below the line into `docs/handoff/[spec-id]/SPEC.md` and fill it in. Square brackets mark
what you replace; the linter rejects any that are left. Lint with
`python3 scripts/check_handoff.py lint docs/handoff/[spec-id]/SPEC.md` until it reports no error.

---

# Spec: [one line, what the executor builds]

- Spec-ID: [kebab-case id, same as the directory]
- Status: draft
- Round: 1/3
- Base: [full commit SHA the executor starts from]
- Executor: [model and tool, for the record]

## Goal

[Business goal in one line. Feature goal in one line. The criterion that shows it works, in one line. This is
orientation for the executor, not permission to redesign.]

## Scope

[What this package delivers, as a short list.]

## Out of scope

[What the executor must not build even if it looks related: neighbouring features, refactors, other
packages of the same feature.]

## Files

| Path | Action | Purpose |
|---|---|---|
| `[path]` | create | [one line] |
| `[path]` | modify | [one line] |

## Protected files

The acceptance tests and anything else the executor must not change. Fill the hashes with
`check_handoff.py hash [files]` after the tests are committed.

| Path | sha256 |
|---|---|
| `[tests/path]` | [64 hex characters] |

## Context

[Everything the executor needs and cannot be trusted to find: the current text of each block it changes,
quoted exactly with the file and a nearby unique line; the signatures it calls; the existing pattern to
copy, quoted; the commands to run tests, linters and the app; the meaning of each project term.]

## Steps

### S1 [short title]

**Change:** [the exact edit: file, the unique text to find, what replaces it, or the full content of a new
file in a fenced block. Name every identifier.]
**Check:** `[one command]`
**Expect:** [exact output, exit code or count]

### S2 [short title]

**Change:** [...]
**Check:** `[...]`
**Expect:** [...]

## Acceptance

```sh
[the commands that must pass at the end, normally the protected tests plus lint and type checks]
```

Expect: [exact result, for example "14 passed, 0 failed" and exit code 0 for each command].

## Stop and ask

[The places where this spec knows it could be wrong: an anchor that may have moved, a value that depends on
data, a library call whose version you could not pin. Say what the executor checks and that it stops when
the check differs.]

## Report

Write `REPORT.md` next to this spec with these sections:

- `## Steps`: one line per step id: done, blocked or not started.
- `## Checks`: per step the Check command and the last lines of its output; then each Acceptance command
  with its output.
- `## Deviations`: every place the result differs from the spec, or `none`.
- `## Questions`: per question: Step, What is missing, What I checked, Options I see, What I would do; or
  `none`.

## Executor rules

<!-- executor-rules:begin -->
You are the executor of this spec. Every design decision is already made in it.
1. Do the steps in order. After each step run its Check and compare the output with its Expect. Start
   the next step only when they match.
2. Change only the files in the Files table. Never edit a file in the Protected files table. Never add,
   remove or upgrade a dependency, and never touch configuration, CI or lock files unless the Files
   table lists them.
3. Use only names (files, functions, classes, routes, flags, keys, packages) that appear in this spec or
   that a search in the repository showed you. Never invent an API.
4. Do not redesign, rename, refactor, reformat or improve anything the steps do not ask for, even when
   you think it is better.
5. Stop and ask when: the text a step says to find is not there exactly; a Check fails twice and the
   second output told you nothing new; you need a file, name, value or dependency the spec does not
   give; a step can be read two ways; a protected test fails for a reason you cannot explain. Write
   the question under Questions in the report as: Step, What is missing, What I checked, Options I
   see, What I would do. Then continue only with steps that do not depend on the answer. Never guess
   to keep going; a precise question is a good result.
6. Never make a failure disappear: no skipped or deleted test, no ignore comment, no catch-all, no
   "|| true", no looser type, no disabled check.
7. Never push, deploy, publish, send messages, run migrations against a shared database, or read
   secrets. Work only in the checkout you were given.
8. Write the report in the format of the Report section: each step as done, blocked or not started,
   with the Check command and the last lines of its output. A step is done only when its Expect
   matched. List every deviation from the spec, or write "none".
<!-- executor-rules:end -->
