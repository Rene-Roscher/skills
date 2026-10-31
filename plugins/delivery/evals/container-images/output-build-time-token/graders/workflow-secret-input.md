---
type: regex
pattern: '^\s*(secrets|secret-envs):'
flags: m
target:
  source: file
  path: .github/workflows/image.yml
---
