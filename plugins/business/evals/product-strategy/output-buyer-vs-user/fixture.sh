#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
cat > README.md <<'MD'
# Shift planner

A mobile app with a drag-and-drop dashboard where bar managers assign staff to shifts. It sends push
notifications, has an AI scheduler that fills the week automatically and a screen for swapping shifts.
We think restaurants and bars will love it.

Notes from the founder: the people who sign up are the restaurant owners. The people who would open it every
day are waiters and bartenders, many of them part-time and on their own phones.
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
