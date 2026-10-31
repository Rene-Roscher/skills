---
description: "Should trigger dual-key-identifiers (validation split). Run with --ablation none."
tags: [dual-key-identifiers, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We send webhook payloads with `user_id: 42`. Anything wrong with that?
