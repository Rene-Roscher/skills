---
description: "Near miss for interface-motion (train): data loading belongs to vue-inertia-frontend. Run with --ablation none."
tags: [interface-motion, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The revenue widget on the dashboard loads slowly. Load it on its own after the page renders.
