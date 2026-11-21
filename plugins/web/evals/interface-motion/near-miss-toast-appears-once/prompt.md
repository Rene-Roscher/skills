---
description: "Near miss for interface-motion (train): browser test mechanics belong to browser-verification. Run with --ablation none."
tags: [interface-motion, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a Playwright test that waits for the invite toast and asserts it appears exactly once.
