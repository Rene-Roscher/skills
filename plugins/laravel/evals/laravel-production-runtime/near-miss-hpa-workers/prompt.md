---
description: Must not trigger; infrastructure manifests. Run with --ablation none.
tags: [laravel-production-runtime, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a Kubernetes HPA for the queue workers.
