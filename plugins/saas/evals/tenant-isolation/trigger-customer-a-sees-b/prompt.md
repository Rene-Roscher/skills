---
description: "Should trigger tenant-isolation (train split). Run with --ablation none."
tags: [tenant-isolation, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Can a user of customer A see customer B's invoices through the API? Check it.
