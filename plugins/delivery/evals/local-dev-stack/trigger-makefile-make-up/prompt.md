---
description: "Should invoke local-dev-stack (validation split). Run with --ablation none."
expected_outcome: "The local-dev-stack skill is invoked."
tags: [local-dev-stack, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a Makefile so that `make up` starts our whole local stack, runs the migrations and then starts the workers.
