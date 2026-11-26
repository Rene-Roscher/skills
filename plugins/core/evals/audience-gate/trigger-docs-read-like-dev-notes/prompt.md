---
description: Should load audience-gate. Validation split. Run with --ablation none --threshold 0.5.
tags: [audience-gate, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

A customer told us our help pages read like developer notes, things like 'according to the config' and 'internally this is a job'. Audit them.
