---
type: regex
pattern: 'octane-scan:\s*allow'
match: not_contains
target:
  source: file
  path: app/Reports/ReportScope.php
weight: 3
---
