---
description: "Near miss, must not trigger plan-entitlements (train split): pricing. Run with --ablation none."
tags: [plan-entitlements, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

What should our Team plan cost per month, given hosting costs of about 4 euros per customer?
