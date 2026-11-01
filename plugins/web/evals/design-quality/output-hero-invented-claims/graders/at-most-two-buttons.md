---
type: regex
pattern: '(?:class="btn"[\s\S]*){3}'
match: not_contains
target:
  source: file
  path: public/index.html
weight: 1
---
