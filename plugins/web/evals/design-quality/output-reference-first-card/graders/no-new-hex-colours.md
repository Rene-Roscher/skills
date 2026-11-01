---
type: regex
pattern: '#[0-9a-fA-F]{3,8}\b'
match: not_contains
target:
  source: file
  path: public/settings.html
weight: 2
---
