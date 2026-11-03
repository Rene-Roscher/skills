---
type: regex
pattern: '(?i)speicherung|durchgeführt|durchführung|\berfolgt\b|kreier'
match: not_contains
weight: 2
target:
  source: file
  path: copy/ui-texte.md
---
