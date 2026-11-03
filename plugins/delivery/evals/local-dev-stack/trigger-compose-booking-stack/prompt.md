---
description: "Should invoke local-dev-stack (train split). Run with --ablation none."
expected_outcome: "The local-dev-stack skill is invoked."
tags: [local-dev-stack, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Set up a Docker Compose dev environment for our booking system: PostgreSQL, Redis, one queue worker and the scheduler.
