#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/plans docs/specs app/database/migrations app/database/seeders app/config app/routes
cat > docs/plans/2026-10-28-inception.md <<'MD'
# Inception: Studio booking

Status: Approved
Approved-by: owner, 2026-10-30
MD
cat > docs/specs/architecture.md <<'MD'
# Architecture

Status: Approved

One component: a Laravel web app in app/ (Laravel Vue starter kit, PostgreSQL 17, Pest).
MD
cat > docs/specs/runtime.md <<'MD'
# Runtime

Status: Approved

- Queue, cache and sessions run on Redis 8 (one instance, separate databases). No database queue, cache or
  session driver.
- The app sends no email in version 1: sign-in is by passkey, password reset is not offered.
- No job batches.
MD
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

## Scaffold

| Component | Directory | Starter | Version | Flags |
|---|---|---|---|---|
| App | app | Laravel Vue starter kit | installer 5.32.0, laravel/framework 13.17 | --vue --pest --database=pgsql --pnpm --no-boost |
MD
cat > app/composer.json <<'JSON'
{"require": {"php": "^8.4", "laravel/framework": "^13.17", "inertiajs/inertia-laravel": "^3.0", "laravel/fortify": "^1.37"}}
JSON
cat > app/.env.example <<'ENV'
APP_NAME=Laravel
DB_CONNECTION=pgsql
SESSION_DRIVER=database
QUEUE_CONNECTION=database
CACHE_STORE=database
MAIL_MAILER=log
ENV
for spec in "0001_01_01_000000_create_users_table:users password_reset_tokens sessions" \
            "0001_01_01_000001_create_cache_table:cache cache_locks" \
            "0001_01_01_000002_create_jobs_table:jobs job_batches failed_jobs"; do
  file=${spec%%:*}; tables=${spec#*:}
  {
    echo "<?php"; echo; echo "return new class extends Illuminate\\Database\\Migrations\\Migration {"
    echo "    public function up(): void {"
    for t in $tables; do echo "        Schema::create('$t', function (\$table) { \$table->id(); });"; done
    echo "    }"; echo "};"
  } > "app/database/migrations/$file.php"
done
cat > app/database/seeders/DatabaseSeeder.php <<'PHP'
<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        User::factory()->create(['name' => 'Test User', 'email' => 'test@example.com']);
    }
}
PHP
cat > app/config/queue.php <<'PHP'
<?php

return [
    'default' => env('QUEUE_CONNECTION', 'database'),
    'batching' => ['database' => env('DB_CONNECTION', 'sqlite'), 'table' => 'job_batches'],
    'failed' => ['driver' => env('QUEUE_FAILED_DRIVER', 'database-uuids'), 'table' => 'failed_jobs'],
];
PHP
printf "<?php\n\nRoute::inertia('/', 'Welcome')->name('home');\n" > app/routes/web.php
git add -A
git -c user.email=t@example.org -c user.name=t commit -qm "chore: scaffold app from the Laravel Vue starter kit 13.17"
