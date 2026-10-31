---
type: regex
pattern: '\bnpm (install|i)\b'
match: not_contains
target:
  source: file
  path: Dockerfile
---
