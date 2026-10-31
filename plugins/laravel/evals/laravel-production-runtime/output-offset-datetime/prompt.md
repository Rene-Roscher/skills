---
description: A datetime with an offset is converted to UTC before Eloquent sees it, and a test sends an offset. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: The fix converts the parsed value to UTC before assignment, a new test sends +01:00 and asserts 09:00 UTC, and the reply says the offset is dropped when Eloquent formats the value.
tags: [laravel-production-runtime, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Fix this bug in our booking API: `starts_at` sent as `2026-03-01T10:00:00+01:00` is stored as 10:00 UTC instead of 09:00 UTC.
