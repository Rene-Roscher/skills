---
type: regex
pattern: 'gradient|text-shadow|box-shadow\s*:'
match: not_contains
target:
  source: file
  path: public/settings.html
weight: 1
---
