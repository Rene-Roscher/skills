---
type: regex
pattern: 'schedule:work|while\s+(true|:)'
match: not_contains
weight: 3
target:
  source: file
  path: compose.prod.yaml
---
