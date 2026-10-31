---
description: A job that wakes a person goes on its own queue, away from bulk work, with a test on the queue name. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: SendFraudAlert is dispatched to a dedicated queue that the newsletter does not use, a test asserts that queue name, and the reply says a separate worker must process that queue and why FIFO bulk work would delay it.
tags: [laravel-production-runtime, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a queued job `app/Jobs/SendFraudAlert.php` that texts the analyst on duty when a payment is flagged, plus a test. The weekly newsletter job already runs on the default queue.
