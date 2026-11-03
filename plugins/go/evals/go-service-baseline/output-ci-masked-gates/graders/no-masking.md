---
type: regex
pattern: '\|\|\s*true|continue-on-error:\s*true'
match: not_contains
weight: 2
target:
  source: file
  path: .github/workflows/ci.yml
---
