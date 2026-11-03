---
description: "Near miss, must not trigger tenancy-model (train split): tenant-isolation. Run with --ablation none."
tags: [tenancy-model, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a global scope so tenant A's tasks never show up in tenant B's API responses.
