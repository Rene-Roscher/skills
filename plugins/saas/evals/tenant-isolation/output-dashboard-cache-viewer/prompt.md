---
description: "Per-workspace dashboard cache where members see different project sets. Needs --scaffold."
expected_outcome: "The cache key or tags include the workspace and a fragment of the member's visible project set, writes invalidate through the same tags or keys, and a test shows two members with different visibility get different numbers."
tags: [tenant-isolation, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Cache the per-workspace dashboard numbers for 5 minutes. Some members only see some projects. Reply with the code; do not write files.
