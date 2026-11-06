---
type: regex
pattern: '[\uD83C-\uD83E][\uDC00-\uDFFF]|[\u2600-\u27BF\u2B50\u2B55]'
match: not_contains
target:
  source: file
  path: scripts/deploy.sh
weight: 3
---
