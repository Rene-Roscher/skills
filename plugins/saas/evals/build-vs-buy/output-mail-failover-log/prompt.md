---
description: Mail failover that ends in log must be flagged as silent success. Run with --scaffold.
expected_outcome: The reply warns that a trailing log transport reports every message as sent, replaces it with a visible failure (exception, retry, dead letter, alert), and notes or flags for verification how failover state behaves in long-lived workers.
tags: [build-vs-buy, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Configure mail failover in config/mail.php: our main provider (postmark), then the backup provider (resend), then `log` so nothing gets lost. Show the config change.
