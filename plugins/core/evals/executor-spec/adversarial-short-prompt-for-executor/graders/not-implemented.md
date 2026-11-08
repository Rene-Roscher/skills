---
type: regex
pattern: '(?i)discount'
match: not_contains
weight: 2
target:
  source: file
  path: src/invoice.py
---
