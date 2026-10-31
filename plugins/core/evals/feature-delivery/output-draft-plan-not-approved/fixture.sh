#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/plans src/projects tests
cat > docs/plans/2026-01-10-exports.md <<'MD'
# CSV export of tasks

Status: Draft
Approved-by:

## Goal

Members can download the tasks of one project as a CSV file.

## Steps

| # | Step | Done when |
|---|---|---|
| 1 | Export service streams the tasks of one project | unit test for column order |
| 2 | Route GET /projects/{project}/tasks.csv | feature test, 404 for a project of another workspace |
| 3 | Export button on the project page | visible only with the export permission |

## Open decisions

1. Include archived tasks? Recommendation: no.
2. Who may export, every member or only admins? Recommendation: admins only.

## Deviations

None yet.
MD
cat > src/projects/tasks.py <<'PY2'
from dataclasses import dataclass


@dataclass
class Task:
    public_id: str
    project_id: int
    title: str
    archived: bool = False
PY2
touch src/__init__.py src/projects/__init__.py tests/__init__.py
