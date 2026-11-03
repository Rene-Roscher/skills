---
description: "Near miss, must not trigger plan-entitlements (validation split): authorization-rbac. Run with --ablation none."
tags: [plan-entitlements, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Which role should be allowed to open the billing settings page?
