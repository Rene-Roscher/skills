---
type: regex
pattern: 'reuseExistingServer:\s*true|127\.0\.0\.1:8000'
match: not_contains
target:
  source: file
  path: playwright.config.ts
weight: 2
---
