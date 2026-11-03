---
type: regex
pattern: '(?i)\bups\b|hoppla|leider|ein fehler ist aufgetreten|zu einem späteren zeitpunkt|ganz schön leer|starte jetzt durch|potenzial|freischalten|^\s*mehr erfahren\s*$'
flags: m
match: not_contains
weight: 3
target:
  source: file
  path: copy/ui-texte.md
---
