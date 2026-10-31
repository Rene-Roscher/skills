#!/usr/bin/env bash
set -euo pipefail
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.0.0" } ] }
JSON
