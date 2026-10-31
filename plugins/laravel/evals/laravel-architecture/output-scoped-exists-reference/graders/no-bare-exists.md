---
type: regex
pattern: 'exists:products'
match: not_contains
target:
  source: file
  path: app/Domains/Invoicing/FormRequests/StoreInvoiceLineRequest.php
weight: 1
---
