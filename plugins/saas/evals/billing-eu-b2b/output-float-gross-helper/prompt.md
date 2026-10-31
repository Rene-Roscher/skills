---
description: A float gross-price helper must become integer arithmetic with the rate as a parameter. Run with --scaffold.
expected_outcome: The reply writes the helper with integer or exact arithmetic, takes the rate as a parameter, does not return round(net * 1.19), and mentions that float rounding differs between PHP 8.3 and 8.4 or that the runtime version must match production.
tags: [billing-eu-b2b, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a helper to our billing code: gross = round(net * 1.19). Net is in cents. Show the code.
