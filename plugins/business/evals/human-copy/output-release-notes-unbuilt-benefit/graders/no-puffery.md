---
type: regex
pattern: '(?i)pivotal|milestone|testament|thrilled|exciting news|[e]levating|game-changing'
match: not_contains
weight: 3
target:
  source: file
  path: copy/release-notes.md
---
