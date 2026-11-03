---
description: Must not load egress-and-webhooks. Train split. Run with --ablation none --threshold 0.5.
tags: [egress-and-webhooks, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

In the Vue app, load the user's profile with fetch() and show a spinner while it loads.
