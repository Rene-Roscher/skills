#!/bin/sh
set -eu
mkdir -p .github/workflows resources/js
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "predis/predis": "^2.0", "inertiajs/inertia-laravel": "^2.0" } }
JSON
printf '#!/usr/bin/env php\n<?php\n' > artisan
cat > package.json <<'JSON'
{ "private": true, "dependencies": { "vue": "^3.5.0", "@inertiajs/vue3": "^2.0.0" } }
JSON
cat > compose.yaml <<'YAML'
services:
  db:
    image: postgres:17
  cache:
    image: redis:7
YAML
cat > .env.example <<'ENV'
DB_CONNECTION=pgsql
CACHE_STORE=redis
ENV
cat > .github/workflows/ci.yml <<'YAML'
name: ci
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: php artisan test
YAML
