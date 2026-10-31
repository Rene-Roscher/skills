---
description: Should load verify-before-done. Validation split. Run with --ablation none --threshold 0.5.
tags: [verify-before-done, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a guard test so nobody queries tenant tables without the tenant scope.
