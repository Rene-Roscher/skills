---
type: regex
pattern: '"(?:motion|@vueuse/motion|gsap|framer-motion|popmotion|animejs|@formkit/auto-animate)"'
match: not_contains
target:
  source: file
  path: package.json
weight: 2
---
