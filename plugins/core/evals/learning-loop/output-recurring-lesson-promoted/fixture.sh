#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/lessons db/migrations
cat > AGENTS.md <<'MD'
# Invoicing app

Tests are Python: run them with `python3 -m unittest discover tests`.

Agent lessons live in `docs/lessons/`. Read `docs/lessons/INDEX.md` before acting and open the lessons that match your task.
MD
cat > docs/lessons/INDEX.md <<'MD'
# Lessons

- [Money is integer cents](money-integer-cents.md): any new amount column or field
MD
cat > docs/lessons/money-integer-cents.md <<'MD'
---
name: money-integer-cents
description: Money is stored and computed as integer cents in invoices, payments and credits
type: feedback
---

Money is integer cents. Never use float, real or double for an amount.

**Why:** Twice a migration added an amount as a float column and sums drifted by a cent on large invoices. (2026-06-02)

**How to apply:** Any new amount column or field in `db/migrations`: use `BIGINT` and a `_cents` suffix.
MD
printf 'CREATE TABLE invoices (id BIGSERIAL PRIMARY KEY, amount_cents BIGINT NOT NULL);\n' > db/migrations/001_create_invoices.sql
printf 'ALTER TABLE invoices ADD COLUMN credit_amount FLOAT NOT NULL DEFAULT 0;\n' > db/migrations/002_add_credits.sql
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
