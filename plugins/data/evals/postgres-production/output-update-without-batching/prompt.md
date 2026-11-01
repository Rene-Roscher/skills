---
description: A migration that adds a column and backfills every row with one UPDATE in the same transaction must be split: DDL separate, backfill in batches with WHERE, one commit per batch. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent flags the UPDATE without WHERE and the DDL plus data change in one transaction, and proposes or writes a batched backfill by key range with one commit per batch as a separate step, and keeps the ALTER short under lock_timeout.
tags: [postgres-production, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

db/migrations/0215_add_currency.sql adds a currency column to orders (150 million rows) and fills it. Our deploy runs each migration file in one transaction. Rework it so it is safe on production.
