---
type: regex
pattern: '(?i)s[e]amless|rob[u]st|lev[e]rag|cutting-[e]dge|state-of-the-art|compr[e]hensive|emp[o]wer|str[e]amlin|best-in-class|world-class|industry-leading|enterprise-grade|\bsolutions?\b|utili[sz]|effortl[e]ss|unparalleled|elev[a]te|facilitat|optimi[sz]e'
match: not_contains
weight: 3
target:
  source: file
  path: copy/payments.md
---
