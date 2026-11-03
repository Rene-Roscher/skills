---
type: regex
pattern: 'go test[^\n]*-race'
weight: 2
target:
  source: file
  path: .github/workflows/ci.yml
---
