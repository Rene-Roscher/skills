---
type: regex
pattern: 'cosign sign-blob[^\n]*SHA256SUMS'
weight: 2
target:
  source: file
  path: .github/workflows/release.yml
---
