---
type: regex
pattern: '<section class="card"[^>]*>\s*<h2>\s*Payment reminders'
flags: i
target:
  source: file
  path: public/settings.html
weight: 2
---
