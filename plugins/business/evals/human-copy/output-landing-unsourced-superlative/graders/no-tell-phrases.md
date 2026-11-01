---
type: regex
pattern: '(?i)[s]eamless|[r]obust|[c]utting-edge|[e]mpower|in today''s|not just a metric|peace of mind|ensuring a|flawless'
match: not_contains
weight: 3
target:
  source: file
  path: copy/landing.md
---
