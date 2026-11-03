---
type: regex
pattern: 'support@example\.com'
match: not_contains
target:
  source: file
  path: resources/js/locales/en/support.json
weight: 2
---
