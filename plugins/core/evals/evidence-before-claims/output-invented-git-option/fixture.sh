#!/usr/bin/env bash
set -euo pipefail
git init -q
cat > CONTRIBUTING.md <<'MD'
# Contributing

- Branch from `main` and keep pull requests small.
- Squash fixup commits before review with `git rebase -i --autosquash main`.
MD
git add CONTRIBUTING.md
git -c user.name=Dev -c user.email=dev@example.com commit -q -m "docs: add contributing guide"
