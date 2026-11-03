---
description: "Should trigger plan-entitlements (train split). Run with --ablation none."
tags: [plan-entitlements, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The free plan allows 3 projects and Pro is unlimited. Where and how should we check this?
