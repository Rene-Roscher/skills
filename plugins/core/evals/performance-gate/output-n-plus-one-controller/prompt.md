---
description: "A list controller with two queries per row and no pagination; the gate reports findings in the fixed format with a formula in N. Run with --scaffold."
expected_outcome: Reports the per-row owner load and per-row task count with path:line, the magnitude as about 2N + 1 queries with a number at a large N, the unbounded get(), and fixes (eager load owner columns, withCount with a condition, pagination) plus a query-budget test with a frozen clock that is constant in N.
tags: [performance-gate, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Run the performance gate on app/Http/Controllers/ProjectController.php before I hand the projects list over. Report the findings; do not change files.
