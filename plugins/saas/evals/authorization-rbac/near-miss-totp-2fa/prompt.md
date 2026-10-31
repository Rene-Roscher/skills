---
description: "Near miss, must not trigger authorization-rbac (train split): authentication. Run with --ablation none."
tags: [authorization-rbac, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add 2FA via TOTP to login.
