#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
printf '# Venue tickets\n' > README.md
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
