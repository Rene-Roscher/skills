---
type: regex
pattern: '^permissions:\s*(\{\s*\}|contents:\s*read)'
flags: m
weight: 2
target:
  source: file
  path: .github/workflows/release.yml
---
