---
type: regex
pattern: 'UPDATE\s+orders\s+SET\s+currency\s*=\s*.EUR.\s*;'
flags: i
weight: 2
match: not_contains
target:
  source: file
  path: db/migrations/0215_add_currency.sql
---
