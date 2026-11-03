---
description: Should load egress-and-webhooks. Validation split. Run with --ablation none --threshold 0.5.
tags: [egress-and-webhooks, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Allow importing a CSV by entering its URL instead of uploading the file.
