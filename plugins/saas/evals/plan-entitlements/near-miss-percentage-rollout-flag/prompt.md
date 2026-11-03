---
description: "Near miss, must not trigger plan-entitlements (validation split): feature flags. Run with --ablation none."
tags: [plan-entitlements, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Roll out the new invoice editor to 10 percent of users behind a feature flag.
