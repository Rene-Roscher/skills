---
description: "Should trigger performance-gate (validation split). Run with --ablation none."
tags: [performance-gate, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Check the CSV export job for memory and query cost before it goes to the queue workers.
