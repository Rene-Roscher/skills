---
description: "Should trigger authorization-rbac (train split). Run with --ablation none."
tags: [authorization-rbac, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add an endpoint to create API tokens with a chosen list of permissions.
