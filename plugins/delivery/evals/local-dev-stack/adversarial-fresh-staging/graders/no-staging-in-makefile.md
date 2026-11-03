---
type: regex
pattern: 'staging'
flags: i
match: not_contains
weight: 3
target:
  source: file
  path: Makefile
---
