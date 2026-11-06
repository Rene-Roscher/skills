---
type: regex
pattern: '"(moment|moment-timezone|vue-toastification|vue3-toastify|notivue)"'
match: not_contains
target:
  source: file
  path: package.json
weight: 3
---
