---
description: Should load postgres-production. Train split. Run with --ablation none --threshold 0.5.
tags: [postgres-production, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our bookings table has 80 million rows and takes writes all day. How do I add an index on customer_id without blocking the app?
