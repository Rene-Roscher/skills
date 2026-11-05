#!/bin/sh
# Freshly scaffolded Laravel starter kit; the runtime spec chose Valkey for queue, cache and session.
set -eu
mkdir -p database/migrations database/seeders docs/specs tests/Feature
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^13.0", "laravel/fortify": "^1.37", "laravel/tinker": "^3.0" } }
JSON
cat > .env.example <<'ENV'
APP_NAME=Ledger
DB_CONNECTION=pgsql
SESSION_DRIVER=database
QUEUE_CONNECTION=database
CACHE_STORE=database
MAIL_MAILER=log
ENV
for m in 0001_01_01_000000_create_users_table 0001_01_01_000001_create_cache_table 0001_01_01_000002_create_jobs_table 2024_01_01_000000_create_passkeys_table; do
  printf '<?php\n// %s from the starter kit\n' "$m" > "database/migrations/$m.php"
done
printf '<?php\n// creates users, password_reset_tokens, sessions\n' >> database/migrations/0001_01_01_000000_create_users_table.php
printf '<?php\n// creates cache, cache_locks\n' >> database/migrations/0001_01_01_000001_create_cache_table.php
printf '<?php\n// creates jobs, job_batches, failed_jobs\n' >> database/migrations/0001_01_01_000002_create_jobs_table.php
printf '<?php\n// seeds a Test User\n' > database/seeders/DatabaseSeeder.php
cat > docs/specs/runtime.md <<'MD'
# Runtime (Approved)

- Database: PostgreSQL 17.
- Queue, cache and sessions: Valkey through PhpRedis, separate connections for queue and session.
- Mail: transactional provider over its API.
- Sign-in: Fortify with passkeys and two-factor authentication.
MD
git init -q . && git add -A && git -c user.email=a@example.com -c user.name=a commit -qm "chore: scaffold app from the Laravel Vue starter kit v13.17"
