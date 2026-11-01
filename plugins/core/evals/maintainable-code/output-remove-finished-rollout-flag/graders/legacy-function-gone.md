---
type: regex
pattern: 'legacy_total'
flags: i
weight: 3
match: not_contains
target:
  source: file
  path: src/checkout.py
---
