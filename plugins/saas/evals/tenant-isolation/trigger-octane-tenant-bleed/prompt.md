---
description: "Should trigger tenant-isolation (validation split). Run with --ablation none."
tags: [tenant-isolation, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We switched to Octane. Could tenant state bleed between requests?
