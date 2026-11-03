---
type: regex
pattern: '^\s*dec\.DisallowUnknownFields\(\)'
flags: m
match: not_contains
weight: 3
target:
  source: file
  path: internal/consume/decode.go
---
