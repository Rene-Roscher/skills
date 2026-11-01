---
type: regex
pattern: '10,000\+|99\.99%|4\.9 out of 5'
match: not_contains
target:
  source: file
  path: public/index.html
weight: 2
---
