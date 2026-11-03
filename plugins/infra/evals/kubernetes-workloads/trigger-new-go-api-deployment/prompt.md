---
description: Should load kubernetes-workloads. Train split. Run with --ablation none --threshold 0.5.
tags: [kubernetes-workloads, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a production Deployment manifest for our Go API container. It listens on 8080 and connects to PostgreSQL.
