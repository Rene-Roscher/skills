---
description: "Invoice endpoint in a Laravel fixture: the resource emits public IDs only and a test proves a foreign invoice is a 404. Needs --scaffold."
expected_outcome: "The resource maps id to public_id and the customer reference to the customer's public ID, never emits the internal key, and the feature test requests another organization's invoice and expects 404."
tags: [dual-key-identifiers, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

In this Laravel app, add `GET /api/v1/invoices/{invoice}` with an API resource and a feature test. Invoices belong to an organization and reference a customer. Reply with the code for each file; do not write files.
