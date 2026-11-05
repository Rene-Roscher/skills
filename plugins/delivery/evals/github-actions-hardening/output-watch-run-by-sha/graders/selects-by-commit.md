---
type: regex
pattern: '(--commit|-c)\s+"?\$|headSha'
weight: 3
target:
  source: file
  path: scripts/ci-watch.sh
---
