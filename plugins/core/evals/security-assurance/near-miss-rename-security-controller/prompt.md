---
description: Must not load security-assurance. Train split. Run with --ablation none --threshold 0.5.
tags: [security-assurance, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename SecurityController to AccountSettingsController and update the three route files that import it.
