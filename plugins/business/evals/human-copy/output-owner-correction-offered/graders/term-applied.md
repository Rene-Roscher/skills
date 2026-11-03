---
type: regex
pattern: '(?i)\bslots?\b'
match: not_contains
weight: 2
target:
  source: file
  path: copy/buchung.md
---
