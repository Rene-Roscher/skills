---
description: "Should invoke local-dev-stack (train split). Run with --ablation none."
expected_outcome: "The local-dev-stack skill is invoked."
tags: [local-dev-stack, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

When I start my second project, its Postgres container fails with "port is already allocated". How should we set up ports so all my projects can run side by side on this machine?
