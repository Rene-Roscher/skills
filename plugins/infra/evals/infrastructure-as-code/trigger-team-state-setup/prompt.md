---
description: Should load infrastructure-as-code. Train split. Run with --ablation none --threshold 0.5.
tags: [infrastructure-as-code, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our OpenTofu state is a gitignored terraform.tfstate on my laptop and a colleague wants to run plans too. How should we set up state for the team?
