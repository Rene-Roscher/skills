# Guard artifacts

## Contents

- Investigation note template
- Tracker settings
- Suppression scan
- Guard tests for scannable bug classes
- Shared guards from other skills

These are copied into the project. Each one turns a rule of this skill into a check.

## Investigation note template

Save as `docs/templates/bug-note.md`, or use it as the issue body template:

```text
## Facts
[facts block from the collect-facts reference]

## Class
[P0 leak | P0 loss or money | P1 | P2 | P3], because [signal]. Owner informed: [time, channel] (P0 only)

## Runtime gate
[output: process start times, build time, HEAD commit time]

## Trigger
[input or state] makes [code] do [wrong thing]

## Reproduction test
[test name]; output without the fix: [first failing line]

## Fix
[what changed, path:line]; red, green, red with the fix reverted: [yes]

## Siblings
[search used]; [n] checked, [m] found; guard: [name]

## Open
[items with links]
```

## Tracker settings

- Bug issues cannot be created without a class. In an issue form, make the class a required field; in other
  trackers, a required label or field.
- Resolving needs a release reference: resolve "in release" or "in next release" in the error tracker, and a
  release or deploy field on the tracker issue.
- A bug moves to done only from review, and only with a note on how the fix was observed in the target
  environment.

## Suppression scan

Save as `scripts/scan-suppression.sh`. It reads a unified diff on stdin and lists added lines that look like
suppression. A hit is a question for review, not a verdict; extend the pattern for the project's languages.

```sh
#!/bin/sh
# Usage: git diff origin/main...HEAD | sh scripts/scan-suppression.sh
set -eu
pattern='catch[[:space:]]*[(][^)]*[)][[:space:]]*[{][[:space:]]*[}]'
pattern="$pattern"'|except[^:]*:[[:space:]]*pass'
pattern="$pattern"'|[=(,][[:space:]]*@[a-z_]+[(]|return[[:space:]]+@[a-z_]+[(]'
pattern="$pattern"'|--force|--no-verify'
pattern="$pattern"'|[.]skip[(]|pytest[.]mark[.]skip|markTestSkipped|@Disabled|t[.]Skip[(]'
pattern="$pattern"'|@ts-ignore|eslint-disable|#[[:space:]]*noqa'
awk -v pat="$pattern" '
  /^\+\+\+ / { file = substr($0, 5); sub(/^b\//, "", file); next }
  /^\+/ && $0 ~ pat { print file ": " substr($0, 2); found = 1 }
  END { if (found) exit 1; print "no suppression patterns in added lines" }
'
```

## Guard tests for scannable bug classes

When the sibling search finds a pattern that a scan can detect, keep it:

- The test scans the source tree for the pattern and fails with the file and line of each hit.
- It ships with a known-positive fixture outside the scanned tree, and a second assertion that the scan flags the
  fixture. Without it, a scan that silently stopped matching passes forever.
- Exceptions use an inline marker with a reason, and the test lists them in its output.

Examples of classes that scan well: a class referenced in a file without its import; a query on a tenant-owned
table without the tenant filter; a money value parsed as a float; a date created without a time zone.

## Shared guards from other skills

- The test-environment transport guard from `safe-actions`: tests fail if mail, SMS, push or payment clients are
  real in the test environment.
- The health gate from `verify-before-done`: process start times against file changes, build time against HEAD.
- The cross-tenant probe from `tenant-isolation`, for every P0 leak, kept as a regression test.
- Optional: coverage on changed lines for bug-fix pull requests, so the fixed branch is executed by a test.
