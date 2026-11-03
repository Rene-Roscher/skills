---
type: regex
pattern: '(?i)\b(?:fastest|best|leading|most (?:secure|reliable|trusted)|trusted by|bank-level|bank-grade|compliant|certified|guarantee[ds]?)\b'
match: not_contains
weight: 2
target:
  source: file
  path: copy/payments.md
---
