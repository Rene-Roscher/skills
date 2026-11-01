---
type: regex
pattern: '(mock\.patch|@patch|monkeypatch|unittest\.mock)'
flags: i
weight: 3
match: not_contains
target:
  source: file
  path: tests/test_reminders.py
---
