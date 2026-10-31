---
description: "Should trigger dual-key-identifiers (train split). Run with --ablation none."
tags: [dual-key-identifiers, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a `GET /api/v1/invoices/{invoice}` endpoint that returns the invoice with its customer.
