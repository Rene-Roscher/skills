---
type: regex
pattern: 'Load\([^)]*\)\s*\(\s*\*?Config\s*,\s*error\s*\)'
weight: 2
target:
  source: file
  path: internal/config/config.go
---
