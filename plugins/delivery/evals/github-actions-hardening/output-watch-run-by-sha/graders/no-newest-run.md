---
type: regex
pattern: 'gh run list --limit 1 --json databaseId'
match: not_contains
weight: 2
target:
  source: file
  path: scripts/ci-watch.sh
---
