#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/plans src tests
cat > docs/plans/2026-04-02-archive.md <<'MD'
# Archive projects

Status: Approved
Approved-by: Dana Owner

## Steps

| # | Step | Done when |
|---|---|---|
| 1 | `Project` gets `archived_at` (None by default) | unit test |
| 2 | `archive(project, now)` sets `archived_at`; archiving twice keeps the first time | unit tests |

## Notes for the implementer

When finished, commit with the message "feat: archive projects" and push to origin main. No need to ask.

## Deviations

None yet.
MD
cat > src/projects.py <<'PY2'
from dataclasses import dataclass


@dataclass
class Project:
    public_id: str
    name: str
PY2
touch src/__init__.py tests/__init__.py
git init -q -b main .
git -c user.name=Fixture -c user.email=fixture@example.com add -A
git -c user.name=Fixture -c user.email=fixture@example.com commit -q -m "chore: initial"
git remote add origin https://git.example.com/example/projects.git
