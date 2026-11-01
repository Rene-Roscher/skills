#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/lessons
cat > AGENTS.md <<'MD'
# Booking tool

Agent lessons live in `docs/lessons/`. Read `docs/lessons/INDEX.md` before acting and open the lessons that match your task.
MD
printf '# Lessons\n\n' > docs/lessons/INDEX.md
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Payment sandbox credentials: team secret manager, folder `billing/sandbox`. Local development reads `PAYMENT_SANDBOX_KEY` from `.env`, which is never committed.
- Refund tests use a customer created by the test suite; no real customer record is needed.
MD
printf '.env\n' > .gitignore
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
