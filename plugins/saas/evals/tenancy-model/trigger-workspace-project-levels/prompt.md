---
description: "Should trigger tenancy-model (train split). Run with --ablation none."
tags: [tenancy-model, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We are adding workspaces and projects to our B2B tool. Which level should own billing, API tokens, members and the actual tasks?
