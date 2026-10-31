---
description: Near miss for build-vs-buy; the skill must not be invoked. Run with --ablation none.
expected_outcome: The build-vs-buy skill is not invoked.
tags: [build-vs-buy, near-miss]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Why is this query slow? SELECT * FROM bookings WHERE customer_id = 42 ORDER BY created_at DESC
