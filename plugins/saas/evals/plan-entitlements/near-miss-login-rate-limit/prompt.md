---
description: "Near miss, must not trigger plan-entitlements (train split): auth throttling. Run with --ablation none."
tags: [plan-entitlements, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Rate-limit the login endpoint to 5 attempts per minute per IP.
