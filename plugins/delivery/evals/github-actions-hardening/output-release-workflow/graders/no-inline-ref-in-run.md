---
type: regex
pattern: 'run:[^\n]*\$\{\{\s*(github\.event|github\.head_ref|github\.ref_name|inputs\.)'
match: not_contains
target:
  source: file
  path: .github/workflows/release.yml
---
