---
description: A migration that adds a foreign key, a CHECK and SET NOT NULL to a large table in one step must be split into NOT VALID then VALIDATE CONSTRAINT, with lock_timeout. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent flags that the foreign key and the NOT NULL scan the table under a lock, rewrites the foreign key with NOT VALID and a separate VALIDATE CONSTRAINT, uses a CHECK (col IS NOT NULL) NOT VALID then VALIDATE route before SET NOT NULL, and sets lock_timeout.
tags: [postgres-production, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Check db/migrations/0107_invoice_constraints.sql. invoices has 200 million rows in production and we cannot take downtime. Make it safe to run.
