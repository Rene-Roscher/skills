---
type: regex
pattern: 'Factory::class|[\x27"]\\?Laravel\\{1,2}Socialite'
match: not_contains
target:
  source: file
  path: config/octane.php
weight: 3
---
