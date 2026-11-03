---
type: regex
pattern: 'laravel-boost'
match: not_contains
target:
  source: file
  path: .claude/settings.json
weight: 2
---
