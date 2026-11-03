---
description: "Must not load search-visibility; pulling and comparing metrics belongs to search-measurement. Run with --ablation none --threshold 0.5."
tags: [search-visibility, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Pull last week's Search Console clicks and impressions for our invoicing app's site and compare them with the week before.
