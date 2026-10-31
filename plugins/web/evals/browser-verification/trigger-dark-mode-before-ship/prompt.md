---
description: "Should trigger browser-verification (validation split). Run with --ablation none."
tags: [browser-verification, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Verify the dark mode of the dashboard before we ship.
