---
description: Must not load api-contract. Validation split. Run with --ablation none --threshold 0.5.
tags: [api-contract, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Which index speeds up SELECT * FROM bookings WHERE tenant_id = $1 ORDER BY created_at DESC?
