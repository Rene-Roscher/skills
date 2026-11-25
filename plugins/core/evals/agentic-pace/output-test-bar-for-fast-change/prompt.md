---
description: A critical change written faster than the owner can read it. The reply must ask for tests that are shown to fail and one injected-failure test per failure mode.
max_turns: 8
timeout_seconds: 300
expected_outcome: Three injected-failure tests, one per row, and a mutation run or hand-broken guard on the refund module.
tags: [agentic-pace, output]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

The refund calculation in our invoicing app was just rewritten by an agent in twenty minutes and I cannot read all of it. The plan's failure-mode table has three rows: the payment provider times out during the refund, the refund job is delivered twice, and the worker dies between writing the credit note and calling the provider. What has to be true about the tests before I accept this? List the tests, do not write them.
