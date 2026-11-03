---
type: regex
pattern: '\b(Ihnen|Ihrer?|Ihre[nms]?|Ihres)\b|\bSie (?:können|haben|erhalten|bekommen|sehen|es|bitte)\b|versuchen Sie'
match: not_contains
weight: 3
target:
  source: file
  path: copy/ui-texte.md
---
