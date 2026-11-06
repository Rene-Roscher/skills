---
description: "A dashboard controller computes six KPIs synchronously for large tenants. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Keeps only the cheap open-task count in the first response, defers the expensive widgets in separate groups with rescue, loads the activity feed when visible, caches each widget per tenant with a TTL by freshness (flexible plus a cold-path lock or precomputed rollups), adds Deferred and WhenVisible with fallbacks in the page, and gives a test plan with the group test and cold and warm query counts.
tags: [laravel-architecture, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Our dashboard takes four seconds to load for big customers, and on Monday mornings the database gets hammered. Make it fast and cheap to run. Facts are in `docs/PROJECT-FACTS.md`.
