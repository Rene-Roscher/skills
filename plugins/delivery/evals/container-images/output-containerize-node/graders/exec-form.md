---
type: regex
pattern: '^(ENTRYPOINT|CMD)\s+\['
flags: m
target:
  source: file
  path: Dockerfile
---
