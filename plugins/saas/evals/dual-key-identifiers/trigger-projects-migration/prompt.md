---
description: "Should trigger dual-key-identifiers (train split). Run with --ablation none."
tags: [dual-key-identifiers, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Create a migration and model for `projects`. Clients will link to them.
