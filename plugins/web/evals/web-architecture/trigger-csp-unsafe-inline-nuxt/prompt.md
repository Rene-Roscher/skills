---
description: "Should trigger web-architecture (train split). Run with --ablation none."
tags: [web-architecture, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our CSP has unsafe-inline for scripts, can we get rid of it with Nuxt?
