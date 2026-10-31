---
description: "Should trigger bug-investigation (train split). Run with --ablation none."
tags: [bug-investigation, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Here's a stack trace from production. What's going on?

```text
TypeError: Cannot read properties of undefined (reading 'total')
    at renderInvoice (src/invoices/render.js:48:21)
    at handler (src/invoices/routes.js:17:12)
```
