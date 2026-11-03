---
description: "Near miss, must not trigger plan-entitlements (train split): billing-eu-b2b. Run with --ablation none."
tags: [plan-entitlements, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Apply reverse charge at checkout for customers with an Austrian VAT ID.
