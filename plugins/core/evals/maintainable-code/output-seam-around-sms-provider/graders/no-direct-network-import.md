---
type: regex
pattern: '(urllib|requests|http\.client)'
flags: i
weight: 2
match: not_contains
target:
  source: file
  path: src/reminders.py
---
