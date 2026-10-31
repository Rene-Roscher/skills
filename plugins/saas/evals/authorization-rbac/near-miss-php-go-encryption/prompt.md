---
description: "Near miss, must not trigger authorization-rbac (validation split): service-boundaries. Run with --ablation none."
tags: [authorization-rbac, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Encrypt payloads between the PHP app and the Go service.
