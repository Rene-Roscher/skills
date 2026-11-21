---
description: "Should trigger interface-motion (train). Run with --ablation none."
tags: [interface-motion, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Check that the booking dialog's entrance doesn't overshoot and behaves the same in Firefox and Safari.
