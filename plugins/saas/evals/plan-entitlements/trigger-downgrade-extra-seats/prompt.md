---
description: "Should trigger plan-entitlements (train split). Run with --ablation none."
tags: [plan-entitlements, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

What should happen to a customer's extra seats when they downgrade to a smaller plan?
