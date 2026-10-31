#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
mkdir -p config
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "sentry/sentry-laravel": "^4.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [
  { "name": "laravel/framework", "version": "v12.10.0" },
  { "name": "sentry/sentry", "version": "4.10.0" },
  { "name": "sentry/sentry-laravel", "version": "4.10.0" }
] }
JSON
cat > .env.example <<'ENV'
APP_ENV=production
SENTRY_LARAVEL_DSN=
ENV
