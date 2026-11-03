---
description: Should load infrastructure-as-code. Train split. Run with --ablation none --threshold 0.5.
tags: [infrastructure-as-code, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

We encrypt all secrets in the repo with SOPS to a single age key. We are about to add two more admins. What should change in .sops.yaml and how we handle keys?
