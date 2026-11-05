---
type: regex
pattern: '🇩🇪|🇬🇧|🇺🇸|🇫🇷|🇪🇺|🇦🇹|🇨🇭|🏳|🏴|🌐'
match: not_contains
target:
  source: file
  path: public/index.html
weight: 3
---
