#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p site/pages docs
cat > README.md <<'MD'
# Marketing site for the booking system

Static site in `site/`. Search Console property: `sc-domain:example.com`. Plausible site id: `example.com`.
Bing Webmaster Tools: `https://www.example.com/` is verified.
MD
cat > site/pages/pricing.html <<'HTML'
<!doctype html><html><head><title>Pricing for venue booking</title></head><body><h1>Pricing</h1></body></html>
HTML
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: add site'
