---
type: regex
pattern: '(?:static|self)::\$\w+|\bstatic\s+(?:\??[\w\\]+\s+)?\$\w+'
match: not_contains
target:
  source: file
  path: app/Billing/PlanResolver.php
weight: 3
---
