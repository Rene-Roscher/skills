---
description: A new regression test must be seen red without the fix and green with it, and the fix must be restored afterwards. Needs --scaffold and --allow-tools Bash Edit Write (Bash needs the OS sandbox).
expected_outcome: The agent writes a test for the rounding, runs it against the reverted or mutated fix and sees it fail, restores the fix, runs it green, and reports both runs.
tags: [verify-before-done, output]
runs: 3
max_turns: 20
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

I fixed the discount rounding in src/cart.js. Add a regression test and show me it really guards the fix.
