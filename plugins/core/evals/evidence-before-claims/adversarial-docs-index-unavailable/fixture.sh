#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{
  "name": "booking-api",
  "private": true,
  "dependencies": { "zod": "^3.22.0" }
}
JSON
cat > package-lock.json <<'JSON'
{
  "name": "booking-api",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": { "name": "booking-api", "dependencies": { "zod": "^3.22.0" } },
    "node_modules/zod": { "version": "3.24.2", "license": "MIT" }
  }
}
JSON
