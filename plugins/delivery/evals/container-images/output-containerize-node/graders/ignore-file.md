---
type: regex
pattern: '(\.env[\s\S]*\.git|\.git[\s\S]*\.env|^\*\*\s*$)'
flags: m
weight: 2
target:
  source: file
  path: .dockerignore
---
