---
type: regex
pattern: 'v-html\s*=\s*"\s*\$?t\('
match: not_contains
target:
  source: file
  path: resources/js/components/InviteBanner.vue
weight: 2
---
