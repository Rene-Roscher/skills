---
type: regex
pattern: 'Open decisions[\s\S]*?(price|pricing|per[- ]call|billing unit|tier)'
flags: i
weight: 1
target:
  source: file
  path: docs/plans/usage-pricing.md
---
