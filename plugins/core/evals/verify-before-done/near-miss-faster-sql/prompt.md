---
description: Must not load verify-before-done. Validation split. Run with --ablation none --threshold 0.5.
tags: [verify-before-done, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Make this SQL query faster: SELECT * FROM bookings WHERE lower(email) = 'user@example.com';
