---
type: regex
pattern: 'cosign verify-blob[\s\S]*certificate-oidc-issuer'
weight: 2
target:
  source: file
  path: .github/workflows/release.yml
---
