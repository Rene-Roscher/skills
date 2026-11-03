---
description: A URL fetcher that checks one resolved IP, then lets requests resolve again and follow redirects without timeouts, must be flagged. Needs --scaffold.
expected_outcome: The agent reads fetcher.py and reports the second resolution (DNS rebinding), unchecked redirects and the missing timeout or size cap, and says it is not safe.
tags: [egress-and-webhooks, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Review fetcher.py. It fetches URLs our users enter. Is the private network protection good enough?
