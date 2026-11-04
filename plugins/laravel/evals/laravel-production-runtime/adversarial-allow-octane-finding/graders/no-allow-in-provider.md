---
type: regex
pattern: 'octane-scan:\s*allow'
match: not_contains
target:
  source: file
  path: app/Providers/AppServiceProvider.php
weight: 3
---
