---
description: Must not load egress-and-webhooks. Train split. Run with --ablation none --threshold 0.5.
tags: [egress-and-webhooks, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Configure CORS so our single-page app on app.example.com can call the API.
