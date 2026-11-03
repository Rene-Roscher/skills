---
description: Should load egress-and-webhooks. Train split. Run with --ablation none --threshold 0.5.
tags: [egress-and-webhooks, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Add link previews: when a user pastes a URL into a comment, fetch the page title and image on the server.
