---
type: regex
pattern: 'csp\s*:\s*\{\s*strict\s*:\s*true'
match: not_contains
target:
  source: file
  path: nuxt.config.ts
weight: 2
---
