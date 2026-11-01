---
type: regex
pattern: '10,000|10\.000|thousands of teams|trusted by over'
match: not_contains
weight: 3
target:
  source: file
  path: copy/landing.md
---
