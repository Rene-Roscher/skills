---
description: "Should trigger performance-gate (train split). Run with --ablation none."
tags: [performance-gate, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We added a 'notify all subscribers' button that also sends SMS. What does one click cost for a tenant with 50,000 subscribers, and will the queue cope?
