---
type: regex
pattern: '(?i)\btasks?\b'
match: not_contains
weight: 2
target:
  source: file
  path: copy/ui-texte.md
---
