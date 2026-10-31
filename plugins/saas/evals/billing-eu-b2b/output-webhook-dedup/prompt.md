---
description: Check-then-insert webhook dedup must become an atomic claim keyed by transition, with re-fetch and a concurrency test. Run with --scaffold.
expected_outcome: The reply replaces exists-then-insert with an atomic insert-on-conflict claim whose key includes the state transition, re-fetches the payment from the provider before acting, and adds a duplicate or concurrent delivery test.
tags: [billing-eu-b2b, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Implement webhook dedup for our payment provider in this app: check whether the event already exists, otherwise insert it and process it. Show the code.
