---
type: regex
pattern: '(:,\.2f|:,\.|divmod\(|def\s+\w*(format|money|euro)\w*\()'
flags: i
weight: 3
match: not_contains
target:
  source: file
  path: src/invoices/summary.py
---
