---
description: "Should trigger authorization-rbac (validation split). Run with --ablation none."
tags: [authorization-rbac, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Map SSO groups to roles on first login.
