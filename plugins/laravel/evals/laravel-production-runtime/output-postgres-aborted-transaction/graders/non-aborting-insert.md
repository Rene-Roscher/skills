---
type: regex
pattern: 'insertOrIgnore|upsert\(|ON CONFLICT|createOrFirst|firstOrCreate|savepoint|DB::transaction\([\s\S]*DB::transaction\('
flags: i
target:
  source: file
  path: app/Domains/Invoicing/Services/RecordPaymentWebhook.php
weight: 3
---
