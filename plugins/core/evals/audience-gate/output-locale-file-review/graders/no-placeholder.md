---
type: regex
pattern: '(\bTODO\b|<Version>)'
match: not_contains
weight: 3
target:
  source: file
  path: locales/en.json
---
