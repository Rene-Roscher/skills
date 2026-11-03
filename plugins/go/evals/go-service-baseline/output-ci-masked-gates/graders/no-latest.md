---
type: regex
pattern: '@latest|version:\s*latest|go-version:\s*stable'
match: not_contains
weight: 2
target:
  source: file
  path: .github/workflows/ci.yml
---
