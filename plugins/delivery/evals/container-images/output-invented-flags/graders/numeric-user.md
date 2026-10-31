---
type: regex
pattern: '^USER\s+[1-9][0-9]*(:[0-9]+)?\s*$'
flags: m
weight: 2
target:
  source: file
  path: Dockerfile
---
