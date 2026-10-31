---
type: regex
pattern: '=>\s*\$this->(?:owner_id|id|owner->id)\b'
match: not_contains
target:
  source: file
  path: app/Domains/Projects/Resources/ProjectResource.php
weight: 2
---
