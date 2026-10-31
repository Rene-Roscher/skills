---
description: "Should trigger browser-verification (train split). Run with --ablation none."
tags: [browser-verification, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a Pest browser test that the restricted user only sees their own projects in the dropdown.
