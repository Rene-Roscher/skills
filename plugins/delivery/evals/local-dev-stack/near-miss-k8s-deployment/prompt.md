---
description: "Must not invoke local-dev-stack; this belongs to a Kubernetes skill (train split). Run with --ablation none."
expected_outcome: "The local-dev-stack skill is not invoked."
tags: [local-dev-stack, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a Kubernetes Deployment and Service for the booking API with readiness and liveness probes.
