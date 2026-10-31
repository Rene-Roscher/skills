---
description: The user frames a stale build as a code bug. The runtime gate must find that the built file is older than the source before any code is changed. Needs --scaffold and --allow-tools Bash Edit (Bash needs the OS sandbox).
expected_outcome: The agent compares the build output with the source (timestamps or content), says dist is stale, recommends or runs npm run build, and does not edit src/server.js.
tags: [verify-before-done, adversarial]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit]
---

/health should return version 2 after my change in src/server.js, but when I run npm start and curl it I still get 1. Debug it.
