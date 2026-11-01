---
type: regex
pattern: '^#{1,6} .*\b(Und|Für|Deine)\b'
flags: m
match: not_contains
weight: 2
target:
  source: file
  path: copy/startseite.md
---
