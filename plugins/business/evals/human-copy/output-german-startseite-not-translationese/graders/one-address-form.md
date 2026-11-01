---
type: regex
pattern: '\b(Ihnen|Ihrer?|Ihre[nms]?)\b|\bSie (?:können|haben|erhalten|bekommen|sehen|richten)\b'
match: not_contains
weight: 3
target:
  source: file
  path: copy/startseite.md
---
