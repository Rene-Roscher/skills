---
description: Should load human-copy for release notes. Train split. Run with --ablation none --threshold 0.5.
tags: [human-copy, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Write the release notes for version 2.4 of our invoicing app from this list: bulk export of invoices, fix for rounding on discounts, new dark theme.
