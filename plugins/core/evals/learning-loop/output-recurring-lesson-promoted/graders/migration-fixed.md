---
type: regex
pattern: 'credit_amount\s+(FLOAT|REAL|DOUBLE)'
flags: i
match: not_contains
weight: 2
target:
  source: file
  path: db/migrations/002_add_credits.sql
---
