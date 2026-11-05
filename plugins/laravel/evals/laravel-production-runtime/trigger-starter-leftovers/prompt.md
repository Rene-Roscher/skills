---
description: "Cleanup after a starter-kit scaffold whose defaults differ from the approved runtime spec. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The agent compares the starter defaults with docs/specs/runtime.md, lists the leftovers (database queue, cache and session drivers and their tables, log mailer, demo seeder) with keep or remove as an owner decision, keeps Fortify features and passkeys, and adds or proposes a schema guard test that asserts the exact table list."
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

The Laravel app is scaffolded from the starter kit. Before we build the first feature, get it in line with our runtime spec. What does the app actually need from what the starter put in?
