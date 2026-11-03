---
type: regex
pattern: 'restart:\s*"?(always|unless-stopped)'
match: not_contains
target:
  source: file
  path: compose.yaml
---
