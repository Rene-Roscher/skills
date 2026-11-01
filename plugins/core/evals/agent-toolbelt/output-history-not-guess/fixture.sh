#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
git config user.name Dev
git config user.email dev@example.com
printf 'RETRY_LIMIT = 3\n' > config.py
git add -A && git commit -q -m "feat: add provider client with retries"
printf '# notes\n' > NOTES.md
git add -A && git commit -q -m "docs: add notes"
printf 'RETRY_LIMIT = 5\n' > config.py
git commit -q -am "fix: raise retry limit to 5, provider times out under load"
printf 'RETRY_LIMIT: int = 5\n' > config.py
git commit -q -am "style: add type annotations to config"
