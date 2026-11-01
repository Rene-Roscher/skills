---
description: Tests for a refund function must cover the allowed case and the refused cases (other tenant, over the paid amount) and check that nothing was stored on refusal. Needs --scaffold and --allow-tools Bash Write.
expected_outcome: The agent writes tests/test_refunds.py with a successful refund, a refund above the paid amount refused, a refund by another tenant refused, and checks the store is unchanged after each refusal. It runs them.
tags: [test-strategy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Write the tests for src/refunds.py into tests/test_refunds.py and run them. Use only the standard library test runner.
