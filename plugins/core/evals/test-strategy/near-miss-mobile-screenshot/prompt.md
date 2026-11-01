---
description: Must not load test-strategy; this belongs to browser-verification. Run with --ablation none --threshold 0.5.
tags: [test-strategy, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Open the login page in a headless browser at 390 pixels width, take a screenshot and check for horizontal overflow.
