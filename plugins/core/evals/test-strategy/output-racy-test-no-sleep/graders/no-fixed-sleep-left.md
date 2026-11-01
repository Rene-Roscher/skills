---
type: regex
pattern: 'time\.sleep\('
flags: i
weight: 3
match: not_contains
target:
  source: file
  path: tests/test_worker.py
---
