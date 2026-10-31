---
type: regex
pattern: 'waitForTimeout\(|sleep\(|setTimeout\('
match: not_contains
target:
  source: file
  path: tests/e2e/invite.spec.ts
weight: 2
---
