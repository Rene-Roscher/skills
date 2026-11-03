---
description: "Should trigger vue-inertia-frontend (train split). Run with --ablation none."
tags: [vue-inertia-frontend, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a deferred activity prop to the dashboard page and show a skeleton until it arrives.
