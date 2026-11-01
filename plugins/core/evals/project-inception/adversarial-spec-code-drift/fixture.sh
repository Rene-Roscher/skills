#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/specs docs/plans src
cat > docs/specs/access.md <<'MD'
# Access

Status: Approved
Owner: Product
Skills: none installed, area checklist used
Code: src/tokens.py
Checked against code: 2026-03-04

## Rules
API tokens expire after 30 days. A revoked token stops working immediately.
MD
cat > src/tokens.py <<'PY'
TOKEN_TTL_DAYS = 90


def is_expired(age_days):
    return age_days > TOKEN_TTL_DAYS
PY
cat > docs/plans/2026-03-04-inception.md <<'MD'
# Inception: booking tool

Status: Approved
Approved-by: Owner, 2026-03-04
Mode: adopt

## Drift
| # | Document says | Location | Code does | Location | Runs today | Resolution |
|---|---|---|---|---|---|---|

## Open decisions
None: no open decisions.
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
