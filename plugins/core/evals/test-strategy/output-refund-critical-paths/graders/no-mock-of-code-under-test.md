---
type: regex
pattern: '(mock|patch)\(.*refund'
flags: i
weight: 1
match: not_contains
target:
  source: file
  path: tests/test_refunds.py
---
