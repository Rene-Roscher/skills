---
type: regex
pattern: 'def\s+send_reminder\([^)]*(sender|sms|gateway|client|notifier|send)'
flags: i
weight: 3
target:
  source: file
  path: src/reminders.py
---
