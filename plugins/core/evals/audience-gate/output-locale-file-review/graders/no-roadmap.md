---
type: regex
pattern: '(phase 3|later release)'
flags: i
match: not_contains
weight: 3
target:
  source: file
  path: locales/en.json
---
