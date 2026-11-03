---
description: Should load agent-delegation. Train split. Run with --ablation none --threshold 0.5.
tags: [agent-delegation, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Tonight I need three things done in the booking system: a scan of all 14 packages for hard-coded API keys, a licence check of every dependency, and a fix to how refunds are prorated. Split it across subagents and tell me which model each one gets.
