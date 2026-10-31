#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
git config user.name Dev
git config user.email dev@example.com
mkdir -p src
printf 'export const rate = 0.19;\n' > src/tax.js
printf '# Shop\n' > README.md
git add -A
git commit -q -m "chore: initial commit"
printf 'export const rate = 0.19;\nexport const roundCents = (v) => Math.floor(v);\n' > src/tax.js
printf '# Shop\n\nRun `npm test` before pushing.\n' > README.md
