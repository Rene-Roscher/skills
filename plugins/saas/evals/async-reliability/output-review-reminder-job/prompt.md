---
description: A Laravel SMS job with timeout above retry_after, dispatch inside a transaction without afterCommit and a paid send under retries must be flagged. Needs --scaffold.
expected_outcome: The agent reads the job and config and reports the timeout versus retry_after conflict, the dispatch before commit, and the duplicate paid send on retry, and says it is not ready.
tags: [async-reliability, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Review app/Jobs/SendReminderSms.php and where it is dispatched. Is it safe to ship?
