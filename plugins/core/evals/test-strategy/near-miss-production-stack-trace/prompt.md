---
description: Must not load test-strategy; this belongs to bug-investigation. Run with --ablation none --threshold 0.5.
tags: [test-strategy, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Here is a stack trace from production: NullPointerException in InvoiceMailer.render at line 88. Why does it crash?
