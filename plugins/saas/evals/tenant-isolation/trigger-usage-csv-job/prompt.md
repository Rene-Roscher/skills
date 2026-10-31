---
description: "Should trigger tenant-isolation (train split). Run with --ablation none."
tags: [tenant-isolation, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a queued job that builds the monthly usage CSV for an organization.
