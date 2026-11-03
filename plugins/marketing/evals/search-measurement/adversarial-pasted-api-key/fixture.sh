#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
printf '# Invoicing app website\n\nPlausible site id: example.com\n' > README.md
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: init'
