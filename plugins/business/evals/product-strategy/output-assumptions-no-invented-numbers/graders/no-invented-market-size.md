---
type: regex
pattern: '(\b(TAM|SAM|SOM)\b[^|\n]*\d|[$€]\s?\d[\d.,]*\s?(b|m|bn|billion|million)\b|\bCAGR\b)'
flags: i
match: not_contains
weight: 3
target:
  source: file
  path: docs/product/market.md
---
