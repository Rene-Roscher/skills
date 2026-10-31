---
description: Must not load verify-before-done. Train split. Run with --ablation none --threshold 0.5.
tags: [verify-before-done, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Here's a stack trace from production, what's going on?

```text
TypeError: Cannot read properties of undefined (reading 'total')
    at renderInvoice (src/invoice.js:42:17)
```
