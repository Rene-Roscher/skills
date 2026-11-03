---
description: "A job that loads all subscribers and sends one SMS each, with retries and no dedupe; the gate states cost per action and the retry risk. Run with --scaffold."
expected_outcome: Reports with path:line the unbounded load of all subscribers, cost per action as recipients times unit price with the numbers given and at 100x, duplicate SMS on retry because sends are not recorded, and fixes (chunked jobs carrying ids, a send record per recipient and announcement checked before sending, a retry test).
tags: [performance-gate, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Gate app/Jobs/NotifySubscribers.php before handover. Our largest tenant has 500 subscribers with phone numbers, and one SMS costs 0.08 EUR. Report the findings only.
