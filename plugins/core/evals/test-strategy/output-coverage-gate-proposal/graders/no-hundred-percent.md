---
type: regex
pattern: '\b100\s*%\s*(global|everywhere|across|of (all|the))'
flags: i
weight: 1
match: not_contains
target:
  source: file
  path: docs/test-gate.md
---
