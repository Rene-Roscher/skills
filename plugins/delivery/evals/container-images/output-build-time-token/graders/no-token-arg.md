---
type: regex
pattern: '^(ARG|ENV)\s+NPM_TOKEN'
flags: m
match: not_contains
weight: 2
target:
  source: file
  path: Dockerfile
---
