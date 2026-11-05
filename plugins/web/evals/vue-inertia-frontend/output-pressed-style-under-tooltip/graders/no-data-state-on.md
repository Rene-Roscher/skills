---
type: regex
pattern: 'data-\[state=on\]'
match: not_contains
target:
  source: file
  path: resources/js/components/PinToggle.vue
weight: 1
---
