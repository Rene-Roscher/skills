---
description: A referenced public ID in a FormRequest is validated against the current tenant, not with a bare exists rule. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: The new FormRequest validates product_id with Rule::exists on the public ID column scoped to the current team, and the reply says a product from another team must fail like an unknown one.
tags: [laravel-architecture, output]
runs: 3
max_turns: 15
timeout_seconds: 450
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a FormRequest for `POST /invoices/{invoice}/lines` in `app/Domains/Invoicing/FormRequests/StoreInvoiceLineRequest.php`. The body has `product_id` (the product's public ID) and `quantity` (integer, at least 1).
