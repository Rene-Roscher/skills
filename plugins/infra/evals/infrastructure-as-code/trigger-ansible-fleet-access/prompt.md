---
description: Should load infrastructure-as-code. Validation split. Run with --ablation none --threshold 0.5.
tags: [infrastructure-as-code, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our ansible.cfg has host_key_checking = False, remote_user = root and one shared private key for the whole fleet. Is that acceptable for production, and what would you change?
