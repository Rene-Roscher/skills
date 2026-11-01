---
type: regex
pattern: '[$€]\s?\d'
match: not_contains
weight: 3
target:
  source: file
  path: docs/product/market.md
---
