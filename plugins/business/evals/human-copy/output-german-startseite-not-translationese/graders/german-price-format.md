---
type: regex
pattern: '€\s?19|19€'
match: not_contains
weight: 1
target:
  source: file
  path: copy/startseite.md
---
