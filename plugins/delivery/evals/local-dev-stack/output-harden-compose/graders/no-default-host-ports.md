---
type: regex
pattern: '^\s*-\s*"?(?:[0-9.]+:)?(5432|6379|8080):'
flags: m
match: not_contains
weight: 2
target:
  source: file
  path: compose.yaml
---
