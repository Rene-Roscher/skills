---
description: A migration with a plain CREATE INDEX on a live table must be flagged and rewritten with CONCURRENTLY, in its own file outside a transaction. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent reads the migration, flags that CREATE INDEX blocks writes, rewrites it with CREATE INDEX CONCURRENTLY, notes that it cannot run inside a transaction block, and mentions checking for an invalid index afterwards.
tags: [postgres-production, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Review db/migrations/0042_index_bookings.sql before we run it on production. The bookings table is large and busy. Fix whatever needs fixing.
