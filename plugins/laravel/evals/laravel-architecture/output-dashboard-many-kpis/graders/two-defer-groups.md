---
type: regex
pattern: 'Inertia::defer\([\s\S]*?[\x27"]([\w-]+)[\x27"]\s*(?:,\s*rescue\s*:\s*true\s*)?\)[\s\S]*Inertia::defer\([\s\S]*?[\x27"](?!\1[\x27"])[\w-]+[\x27"]\s*(?:,\s*rescue\s*:\s*true\s*)?\)'
target:
  source: file
  path: app/Http/Controllers/DashboardController.php
weight: 3
---
