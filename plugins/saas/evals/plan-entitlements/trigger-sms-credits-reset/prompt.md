---
description: "Should trigger plan-entitlements (validation split). Run with --ablation none."
tags: [plan-entitlements, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Each plan includes 25 SMS per month that reset every cycle, but SMS packs customers buy should never expire. Model this.
