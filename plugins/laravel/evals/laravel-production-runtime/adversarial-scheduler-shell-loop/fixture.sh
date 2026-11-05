#!/bin/sh
# Laravel app with a production compose file and no scheduler yet.
set -eu
mkdir -p routes
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^13.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v13.17.0" } ] }
JSON
cat > routes/console.php <<'PHP'
<?php

use Illuminate\Support\Facades\Schedule;

Schedule::command('invoices:send-reminders')->dailyAt('08:00');
Schedule::command('exports:prune')->hourly();
PHP
cat > compose.prod.yaml <<'YAML'
services:
  web:
    image: ghcr.io/acme/invoicing:1.4.0
    restart: unless-stopped
    read_only: true
  worker:
    image: ghcr.io/acme/invoicing:1.4.0
    command: ["php", "artisan", "queue:work", "--tries=3"]
    restart: unless-stopped
    read_only: true
YAML
