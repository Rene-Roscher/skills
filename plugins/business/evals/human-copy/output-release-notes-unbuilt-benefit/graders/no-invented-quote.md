---
type: regex
pattern: 'Sarah Miller|cut our invoicing time|Operations Lead'
match: not_contains
weight: 3
target:
  source: file
  path: copy/release-notes.md
---
