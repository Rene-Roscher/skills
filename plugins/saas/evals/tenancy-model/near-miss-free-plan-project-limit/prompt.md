---
description: "Near miss, must not trigger tenancy-model (validation split): plan-entitlements. Run with --ablation none."
tags: [tenancy-model, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Limit the free plan to 3 projects and block creating the fourth.
