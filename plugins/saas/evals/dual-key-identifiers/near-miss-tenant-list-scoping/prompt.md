---
description: "Near miss, must not trigger dual-key-identifiers (validation split): tenant-isolation. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Make sure tenant A cannot list tenant B's projects.
