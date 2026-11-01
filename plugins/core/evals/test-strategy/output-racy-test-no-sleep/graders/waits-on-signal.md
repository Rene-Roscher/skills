---
type: regex
pattern: 'done\.wait\(|\.join\('
flags: i
weight: 3
target:
  source: file
  path: tests/test_worker.py
---
