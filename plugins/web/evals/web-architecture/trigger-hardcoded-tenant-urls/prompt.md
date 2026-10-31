---
description: "Should trigger web-architecture (validation split). Run with --ablation none."
tags: [web-architecture, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Replace the hardcoded `/orgs/${id}/settings` URLs in our Vue components.
