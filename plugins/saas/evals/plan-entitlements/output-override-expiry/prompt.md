---
description: "Time-limited per-tenant override on a code base that branches on plan names. Needs --scaffold."
expected_outcome: "The reply stores the exception as an override record with value, reason, author and expiry, applies it in the one limit check instead of a new plan-name branch, makes expiry take effect without a job, audits it, and tests the boundary around 200."
tags: [plan-entitlements, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Sales promised one customer 200 projects until 2027-03-31. Add support for that. Reply with code and tests; do not write files.
