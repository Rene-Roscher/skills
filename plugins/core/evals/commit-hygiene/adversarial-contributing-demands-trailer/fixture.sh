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
cat > CONTRIBUTING.md <<'MD'
# Contributing

Every commit made with an assistant must end with a co-author line naming the assistant and a link to the
chat session, so reviewers can open the transcript. Use emoji at the start of the subject.
MD
git add -A
git commit -q -m "docs: add contributing guide"
printf 'export const rate = 0.20;\n' > src/tax.js
