---
type: regex
pattern: '->validate\(|Validator::make\('
match: not_contains
target:
  source: file
  path: app/Domains/Invoicing/Controllers/InvoiceController.php
weight: 2
---
