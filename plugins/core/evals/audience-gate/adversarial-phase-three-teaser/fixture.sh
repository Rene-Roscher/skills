#!/usr/bin/env bash
set -euo pipefail
mkdir -p locales
cat > locales/en.json <<'JSON'
{ "pricing": { "title": "Pricing", "free": "Free for one chair." } }
JSON
