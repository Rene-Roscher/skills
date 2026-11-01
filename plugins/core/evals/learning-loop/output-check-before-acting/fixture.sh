#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/lessons db/migrations scripts
cat > AGENTS.md <<'MD'
# Booking tool

Agent lessons live in `docs/lessons/`. Read `docs/lessons/INDEX.md` before acting and open the lessons that match your task.
MD
cat > docs/lessons/INDEX.md <<'MD'
# Lessons

- [Every migration needs a down file](migrations-need-down.md): any new file in db/migrations
MD
cat > docs/lessons/migrations-need-down.md <<'MD'
---
name: migrations-need-down
description: Every new migration in db/migrations needs a paired down file in the same change
type: feedback
---

A migration without a down file cannot be rolled back, so every new migration ships with one.

**Why:** A release had to be reverted and the migration had no down file, so the rollback was done by hand in production. (2026-08-14)

**How to apply:** For every new `db/migrations/NNN_name.sql`, create `db/migrations/NNN_name.down.sql` in the same change, then run `scripts/check_migrations.sh`; it must exit 0.
MD
printf 'CREATE TABLE bookings (id BIGSERIAL PRIMARY KEY, starts_at TIMESTAMPTZ NOT NULL);\n' > db/migrations/001_create_bookings.sql
printf 'DROP TABLE bookings;\n' > db/migrations/001_create_bookings.down.sql
cat > scripts/check_migrations.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
status=0
for up in db/migrations/*.sql; do
  case "$up" in *.down.sql) continue ;; esac
  down="${up%.sql}.down.sql"
  [ -f "$down" ] || { echo "missing $down" >&2; status=1; }
done
exit $status
SH
chmod +x scripts/check_migrations.sh
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
