#!/bin/sh
set -eu
cat > composer.json <<'JSON'
{
    "name": "example/project-tool",
    "require": { "php": "^8.4", "laravel/framework": "^12.0" }
}
JSON
cat > composer.lock <<'JSON'
{ "packages": [ { "name": "laravel/framework", "version": "v12.53.0" } ] }
JSON
