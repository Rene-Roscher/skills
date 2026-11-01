---
type: regex
pattern: '(?im)^\s*\[?get started\]?\s*$'
match: not_contains
weight: 1
target:
  source: file
  path: copy/landing.md
---
