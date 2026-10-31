#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
cat > composer.json <<'JSON'
{ "require": { "php": "^8.4", "laravel/framework": "^12.0", "laravel/reverb": "^1.0" } }
JSON
cat > composer.lock <<'JSON'
{ "packages": [
  { "name": "laravel/framework", "version": "v12.10.0" },
  { "name": "laravel/reverb", "version": "v1.5.0" }
] }
JSON
mkdir -p worker
cat > worker/go.mod <<'MOD'
module example.com/booking/worker

go 1.24
MOD
cat > worker/main.go <<'GO'
package main

func main() {}
GO
