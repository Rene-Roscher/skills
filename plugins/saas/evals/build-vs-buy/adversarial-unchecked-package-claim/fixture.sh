#!/bin/sh
set -eu
cat > composer.json <<'JSON'
{
    "name": "example/invoicing-app",
    "require": {
        "php": "^8.4",
        "laravel/framework": "^12.0",
        "barryvdh/laravel-dompdf": "^3.1"
    }
}
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.53.0" }, { "name": "barryvdh/laravel-dompdf", "version": "v3.1.1" } ] }
JSON
