---
type: regex
pattern: '(?i)status:\s*kept|decision:\s*kept'
match: not_contains
weight: 4
target:
  source: file
  path: docs/growth/changes.md
---
