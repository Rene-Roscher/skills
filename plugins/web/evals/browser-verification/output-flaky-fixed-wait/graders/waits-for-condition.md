---
type: regex
pattern: 'toHaveCount\(\s*1\s*\)|\.waitFor\(|toBeVisible\(|expect\.poll\('
target:
  source: file
  path: tests/e2e/invite.spec.ts
weight: 2
---
