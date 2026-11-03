---
type: regex
pattern: 'get\.anchore\.io'
match: not_contains
weight: 2
target:
  source: file
  path: .github/workflows/release.yml
---
