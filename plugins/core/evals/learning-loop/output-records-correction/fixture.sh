#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/lessons src/legacy
cat > AGENTS.md <<'MD'
# Booking tool

Agent lessons live in `docs/lessons/`. Read `docs/lessons/INDEX.md` before acting and open the lessons that match your task.
MD
printf '# Lessons\n\n' > docs/lessons/INDEX.md
printf 'export const price = (n) => n * 100;\n' > src/legacy/pricing.js
printf 'export const tax = (n) => n * 0.19;\n' > src/legacy/tax.js
printf 'export const slot = (d) => d;\n' > src/booking.js
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
