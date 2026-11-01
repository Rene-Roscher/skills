#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/lessons
cat > AGENTS.md <<'MD'
# Booking tool

Agent lessons live in `docs/lessons/`. Read `docs/lessons/INDEX.md` before acting and open the lessons that match your task.
MD
cat > docs/lessons/INDEX.md <<'MD'
# Lessons

- [Use npm for installs](use-npm-for-installs.md): any dependency change
MD
cat > docs/lessons/use-npm-for-installs.md <<'MD'
---
name: use-npm-for-installs
description: Install dependencies with npm in this project
type: feedback
---

Use `npm install <package>` for dependency changes and keep a single lockfile.

**Why:** A mixed lockfile state caused a CI failure after a teammate installed with another tool. (2026-02-11)

**How to apply:** Any dependency change: run `npm install <package>` and commit `package-lock.json`.
MD
cat > package.json <<'JSON'
{
  "name": "booking",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "dependencies": {}
}
JSON
printf "lockfileVersion: '9.0'\n" > pnpm-lock.yaml
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
