---
description: "Near miss for browser-verification (validation split): load testing. Run with --ablation none."
tags: [browser-verification, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Load-test the API with 1,000 concurrent users.
