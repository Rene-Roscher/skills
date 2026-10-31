---
type: regex
pattern: '^FROM[\s\S]*\n\s*FROM'
flags: m
target:
  source: file
  path: Dockerfile
---
