---
description: Should load async-reliability. Train split. Run with --ablation none --threshold 0.5.
tags: [async-reliability, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

On-call alerts arrived twenty minutes late during last night's outage. The alert jobs share a queue with the weekly digest mails. What should change?
