---
type: regex
pattern: '(?im)^\s*\[?mehr erfahren\]?\s*$'
match: not_contains
weight: 1
target:
  source: file
  path: copy/startseite.md
---
