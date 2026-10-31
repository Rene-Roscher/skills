---
description: "Near miss, must not trigger dual-key-identifiers (validation split): content slugs are public by design. Run with --ablation none."
tags: [dual-key-identifiers, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a slug field for blog posts on the marketing site.
