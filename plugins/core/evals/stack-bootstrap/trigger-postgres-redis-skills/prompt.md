---
description: "Should trigger stack-bootstrap (validation split). Run with --ablation none."
tags: [stack-bootstrap, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add the Postgres and Redis agent skills to this repo, only for this project and not globally.
