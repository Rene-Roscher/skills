---
description: "Near miss for performance-gate (train split): build speed. Run with --ablation none."
tags: [performance-gate, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Go binary takes 40 seconds to compile. Speed up the build.
