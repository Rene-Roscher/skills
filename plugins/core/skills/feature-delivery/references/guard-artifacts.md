# Guard artifacts

## Contents

- DoD check
- Plan-status check for pull requests
- Architecture tests
- Permission rules for publishing
- Templates the project keeps

These are copied into the project. Each one turns a rule of this skill into a check that fails on its own.

## DoD check

Save as `scripts/lint-dod.py` in the project. It reads a filled checklist (a file, or `-` for stdin): every
top-level bullet is an item, and the next non-blank line must be an indented `met:` or `rejected:` answer.

```python
#!/usr/bin/env python3
"""Fail when a definition-of-done item has no met/rejected answer or a vague one."""
import re
import sys

LINK = re.compile(r"https?://\S+|#\d+|\b[A-Z][A-Z0-9]+-\d+\b")
EMPTY = re.compile(r"^(yes|ok|done|n/?a|not needed|tbd|todo|later)\.?$", re.I)
DEFERRED = re.compile(r"\b(later|tbd|todo|follow[- ]?up)\b", re.I)


def check(lines):
    problems = []
    for i, line in enumerate(lines):
        if not line.startswith("- "):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        m = re.match(r"^\s+(met|rejected):\s*(.*?)\s*$", lines[j]) if j < len(lines) else None
        where = f"line {i + 1}: {line[2:].strip()[:60]}"
        if not m:
            problems.append(f"{where}: no 'met:' or 'rejected:' answer")
            continue
        kind, text = m.groups()
        if not text or EMPTY.match(text):
            problems.append(f"{where}: '{kind}:' needs evidence or a reason")
        elif kind == "rejected" and len(text.split()) < 3:
            problems.append(f"{where}: reason too short")
        elif kind == "rejected" and DEFERRED.search(text) and not LINK.search(text):
            problems.append(f"{where}: deferred without an issue link")
    return problems


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("usage: lint-dod.py FILE|-")
        return 0 if sys.argv[1:] in (["-h"], ["--help"]) else 2
    src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8")
    problems = check(src.read().splitlines())
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

Check the check: the unfilled checklist from `definition-of-done.md` must fail on every item, and an item answered
`rejected: later` must fail.

## Plan-status check for pull requests

Save as `scripts/check-plan-approved.sh`. Feature pull requests carry a line `Plan: docs/plans/[file].md` in their
description; the check fails unless that plan says `Status: Approved` and names an approver.

```sh
#!/bin/sh
# Usage: PR_BODY="$(cat body.md)" sh scripts/check-plan-approved.sh
set -eu
plan=$(printf '%s\n' "${PR_BODY:-}" | tr -d '\r' | sed -n 's/^Plan:[[:space:]]*//p' | head -n 1)
if [ -z "$plan" ]; then echo "description has no 'Plan:' line" >&2; exit 1; fi
case "$plan" in
  /*|*..*) echo "plan path must be relative and stay in the repository: $plan" >&2; exit 1 ;;
esac
[ -f "$plan" ] || { echo "plan file not found: $plan" >&2; exit 1; }
grep -Eq '^Status:[[:space:]]*Approved[[:space:]]*$' "$plan" || { echo "not approved: $plan" >&2; exit 1; }
grep -Eq '^Approved-by:[[:space:]]*[^[:space:]]' "$plan" || { echo "no approver named: $plan" >&2; exit 1; }
echo "approved: $plan"
```

In GitHub Actions, pass the description through `env` (`PR_BODY: ${{ github.event.pull_request.body }}`) and run
the script; never paste the expression into the script text, where the description would run as shell code
(https://docs.github.com/en/actions/reference/security/secure-use, verified 2026-10). Run it on pull requests that
carry the project's feature label, including on the `edited` event so a fixed description re-runs the check.

## Architecture tests

- One write path: a scan over the API controller directory fails on persistence calls on models (save, create,
  update, delete) and passes on calls into domain services. Give it a fixture file with one direct write, which
  must be reported. Architecture-test tools such as Pest `arch()`, ArchUnit or dependency-cruiser can express the
  dependency part of the rule.
- Shared bounds: a test reads each column's length or range from the database catalog (for PostgreSQL,
  `information_schema.columns`) and compares it with the shared validation constant. Run it on the production
  engine; SQLite ignores declared lengths.
- Foreign equals missing: the cross-tenant probe from `tenant-isolation`, run for every resource the feature adds,
  expects 404 for a valid foreign ID and for a random ID, on web and API.

## Permission rules for publishing

Make git publication ask every time, in the project's committed Claude Code settings:

```json
{
  "permissions": {
    "ask": ["Bash(git commit *)", "Bash(git push *)", "Bash(git tag *)"]
  }
}
```

A rule matches the command as written: `git -C . push` is not matched by `Bash(git push *)`
(https://code.claude.com/docs/en/permissions, verified 2026-10). Keep the review habit as well as the rule.

## Templates the project keeps

- The plan template has a `Deviations` section (owned by `feature-planning`). Add it if the project's template
  lacks one.
- `docs/templates/definition-of-done.md`: the checklist from `definition-of-done.md`.
- `docs/templates/completion-report.md`: the template from `completion-report.md`, shared with
  `verify-before-done`.
