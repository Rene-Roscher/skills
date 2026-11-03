---
description: Should load egress-and-webhooks. Train split. Run with --ablation none --threshold 0.5.
tags: [egress-and-webhooks, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Let customers register a webhook URL and send them booking.created events.
