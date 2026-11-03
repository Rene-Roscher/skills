---
description: "Near miss for design-quality: a calculation bug on a billing settings page is logic, not design. Run with --ablation none."
tags: [design-quality, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

On our billing settings page, EU customers with a VAT ID are still shown VAT on the next invoice total. Where should the server decide whether reverse charge applies, and how do I test that rule?
