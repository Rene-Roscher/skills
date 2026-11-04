#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs
cat > docs/GLOSSARY.md <<'MD'
# Glossary

| term | aliases | meaning in this project | not to confuse with | source |
|---|---|---|---|---|
| Buchung | booking | One reserved time slot of a customer | Buchung in the accounting sense | docs/domain.md |
MD
printf '# Shop\n\nProject vocabulary lives in docs/GLOSSARY.md.\n' > README.md
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
