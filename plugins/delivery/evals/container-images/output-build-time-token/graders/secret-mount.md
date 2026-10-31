---
type: regex
pattern: '--mount=type=secret,id=[\w-]+'
weight: 2
target:
  source: file
  path: Dockerfile
---
