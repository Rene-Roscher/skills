---
type: regex
pattern: '(?i)automatic(ally)? retr|payment recovery|never lose revenue'
match: not_contains
weight: 3
target:
  source: file
  path: copy/release-notes.md
---
