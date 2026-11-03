---
description: "Should trigger plan-entitlements (validation split). Run with --ablation none."
tags: [plan-entitlements, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Show 'You have used 8 of 10 projects' on the settings page and block creating projects at the limit.
