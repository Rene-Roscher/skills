---
description: Must not load agent-toolbelt; this belongs to safe-actions. Run with --ablation none --threshold 0.5.
tags: [agent-toolbelt, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Run kubectl apply for the staging manifests now and tell me when the rollout is done.
