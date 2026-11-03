---
description: "Near miss for stack-bootstrap (train split): writing a Dockerfile. Run with --ablation none."
tags: [stack-bootstrap, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a multi-stage Dockerfile for the Go service in cmd/api.
