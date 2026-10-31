---
description: Should load evidence-before-claims. Validation split. Run with --ablation none --threshold 0.5.
tags: [evidence-before-claims, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Add an actions/cache step with the lookup-only option to the CI workflow.
