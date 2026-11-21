---
description: "A drawer on transition: all with ease-in should become a spring without a new dependency. Run with --scaffold --allow-tools Write Edit Bash."
expected_outcome: Replaces transition all and ease-in with a listed property on a spring curve (a linear() token with a fallback), keeps the open and close state, adds a reduced-motion variant and adds no animation package.
tags: [interface-motion, output]
runs: 3
max_turns: 16
timeout_seconds: 500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

The filter drawer feels sluggish when it opens and closes. Make it feel like a native sheet with a spring, without adding a dependency.
