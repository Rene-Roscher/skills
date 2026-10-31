---
description: Should invoke build-vs-buy. Run with --ablation none.
expected_outcome: The build-vs-buy skill is invoked.
tags: [build-vs-buy, trigger]
runs: 3
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

Integrate a second SMS provider as a fallback for the appointment reminders in our booking system.
