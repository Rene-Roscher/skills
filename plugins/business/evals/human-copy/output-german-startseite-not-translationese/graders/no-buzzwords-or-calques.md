---
type: regex
pattern: '(?i)nahtlos|ganzheitlich|maßgeschneidert|mehrwert|[g]amechanger|heutigen schnelllebigen|tauche ein|nicht nur ein nice-to-have|egal ob'
match: not_contains
weight: 3
target:
  source: file
  path: copy/startseite.md
---
