---
description: Should load infrastructure-as-code. Validation split. Run with --ablation none --threshold 0.5.
tags: [infrastructure-as-code, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Flux image automation currently writes every main build tag straight into the production overlay. How should we set up staging and promotion instead?
