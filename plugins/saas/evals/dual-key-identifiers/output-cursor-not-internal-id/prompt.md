---
description: "Cursor pagination requested on the internal id: the change must sort by non-internal columns. Needs --scaffold."
expected_outcome: "The reply orders by created_at with public_id as the tiebreaker before cursorPaginate, explains that the cursor encodes the sort values, and does not order by id."
tags: [dual-key-identifiers, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Convert the activity feed in `ActivityController` to `cursorPaginate()` ordered by id, it's the fastest. Show the changed code.
