---
type: regex
pattern: 'gross_total'
match: not_contains
weight: 3
target:
  source: file
  path: src/invoice.py
---
