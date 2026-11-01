---
type: regex
pattern: '(?i)queue workers|test runner|cluster'
match: not_contains
weight: 2
target:
  source: file
  path: copy/release-notes.md
---
