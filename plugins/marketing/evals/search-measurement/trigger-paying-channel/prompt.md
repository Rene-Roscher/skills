---
description: "Should invoke search-measurement (validation split). Run with --ablation none."
expected_outcome: "The search-measurement skill is invoked."
tags: [search-measurement, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Plausible shows organic search as our biggest source of visitors for the invoicing app. Is organic also the channel that brings our paying customers, and how would we know?
