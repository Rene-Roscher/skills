---
description: "E2E suite that passes test by test but fails on the second full run. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Identifies that the suite reuses the dev server and dev database and that the rate-limit counter survives in the database cache; gives the suite its own port and database, clears the cache in a global setup, and makes the limit configurable for tests, without removing the throttle from the route.
tags: [browser-verification, output]
runs: 3
max_turns: 16
timeout_seconds: 450
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Every test in `tests/e2e/notes.spec.ts` passes on its own, but the full run fails with 429 from the second run on, and my local notes in the dev app get filled with test notes. Fix the setup.
