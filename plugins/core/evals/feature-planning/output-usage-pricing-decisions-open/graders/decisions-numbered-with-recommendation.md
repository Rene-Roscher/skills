---
type: regex
pattern: 'Open decisions[\s\S]*?\n1\.\s[\s\S]*?Recommend'
flags: i
weight: 2
target:
  source: file
  path: docs/plans/usage-pricing.md
---
