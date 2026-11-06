---
type: regex
pattern: '\bz-(?:\d+|\[\d+\])(?![\w-])'
match: not_contains
target:
  source: file
  path: resources/js/components/ProjectSheet.vue
weight: 2
---
