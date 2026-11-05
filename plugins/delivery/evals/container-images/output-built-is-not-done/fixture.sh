#!/usr/bin/env bash
# PHP app image that builds cleanly but drops its arguments and ships a REPL.
set -euo pipefail
mkdir -p docker
cat > composer.json <<'JSON'
{ "name": "acme/booking", "require": { "php": "^8.4", "laravel/framework": "^13.0", "laravel/tinker": "^3.0" },
  "require-dev": { "pestphp/pest": "^4.0", "fakerphp/faker": "^1.24" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v13.17.0" }, { "name": "laravel/tinker", "version": "v3.0.2" }, { "name": "psy/psysh", "version": "v0.12.12" } ],
  "packages-dev": [ { "name": "pestphp/pest", "version": "v4.1.0" } ] }
JSON
cat > docker/entrypoint.sh <<'SH'
#!/bin/sh
set -e
php artisan config:cache
exec frankenphp run --config /etc/caddy/Caddyfile
SH
cat > Dockerfile <<'DOCKERFILE'
# syntax=docker/dockerfile:1
FROM composer:2 AS vendor
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --prefer-dist

FROM dunglas/frankenphp:1-php8.4
WORKDIR /app
COPY --from=vendor /app/vendor ./vendor
COPY . .
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
DOCKERFILE
cat > compose.prod.yaml <<'YAML'
services:
  web:
    image: ghcr.io/acme/booking:latest
    read_only: true
    tmpfs:
      - /app/storage/framework:mode=0700
  worker:
    image: ghcr.io/acme/booking:latest
    command: ["php", "artisan", "queue:work", "--tries=3"]
    read_only: true
YAML
