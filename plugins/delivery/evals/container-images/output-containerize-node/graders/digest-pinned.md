---
type: regex
pattern: '^FROM\s+(--platform=\S+\s+)?\S+@sha256:'
flags: m
weight: 2
target:
  source: file
  path: Dockerfile
---
