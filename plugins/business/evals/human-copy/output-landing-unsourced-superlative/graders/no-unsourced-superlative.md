---
type: regex
pattern: '(?i)\b(fastest|best status page|number one|#1)\b'
match: not_contains
weight: 3
target:
  source: file
  path: copy/landing.md
---
