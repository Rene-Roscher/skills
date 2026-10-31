---
description: "Near miss, must not trigger feature-delivery (train split): belongs to verify-before-done. Run with --ablation none."
tags: [feature-delivery, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a regression test for the bug I fixed.
