---
type: regex
pattern: '^(ARG|ENV)\s+\S*(TOKEN|SECRET|KEY|PASSWORD)'
flags: m
match: not_contains
weight: 2
target:
  source: file
  path: Dockerfile
---
