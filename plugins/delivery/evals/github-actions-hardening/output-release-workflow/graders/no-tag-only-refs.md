---
type: regex
pattern: 'uses:\s*[^\s@#]+@v?\d+(\.\d+)*(\s|$)'
flags: m
match: not_contains
weight: 2
target:
  source: file
  path: .github/workflows/release.yml
---
