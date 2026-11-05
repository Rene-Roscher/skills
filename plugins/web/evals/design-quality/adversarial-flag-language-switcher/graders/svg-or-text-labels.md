---
type: regex
pattern: '<svg|\.svg|>\s*(Deutsch|English|Fran(ç|c)ais|DE|EN|FR)\s*<'
flags: i
target:
  source: file
  path: public/index.html
weight: 2
---
