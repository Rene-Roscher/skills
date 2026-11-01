---
type: regex
pattern: '(from\s+src\.shared\.money\s+import\s+format_money|from\s+\.\.shared\.money\s+import\s+format_money|shared\.money)'
flags: i
weight: 3
target:
  source: file
  path: src/invoices/summary.py
---
