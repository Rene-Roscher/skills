---
description: "Downgrade below current seat usage. Needs --scaffold."
expected_outcome: "The reply never deletes memberships: it deactivates the newest non-owner members above the new limit with a stored reason, never counts or touches the owner, reactivates them on upgrade with the same IDs, and tests the round trip."
tags: [plan-entitlements, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Implement HandlePlanChanged for downgrades: the new plan allows fewer seats than the organization currently has members. Reply with code and tests; do not write files.
