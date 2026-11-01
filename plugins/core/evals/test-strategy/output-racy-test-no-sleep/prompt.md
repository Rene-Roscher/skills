---
description: A test that sleeps a fixed time and fails intermittently must be fixed with an explicit wait on a signal, not a longer sleep or a retry. Needs --scaffold and --allow-tools Bash Edit.
expected_outcome: The agent finds that the test sleeps 50 ms while the job finishes after a random delay, replaces the sleep with a wait on the job's done event with a timeout, runs the test several times, and says why.
tags: [test-strategy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

tests/test_worker.py fails about one run in ten. Fix it properly and show me that it is stable.
