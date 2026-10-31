---
description: A caught unique violation inside a transaction is replaced by an insert that does not abort the PostgreSQL transaction, and the PostgreSQL lane is named. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: The service uses insert-on-conflict, createOrFirst or a savepoint instead of catching the exception and continuing, and the reply names the aborted-transaction rule and the PostgreSQL test config.
tags: [laravel-production-runtime, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

`RecordPaymentWebhook` passes its test on SQLite, but on Postgres the duplicate-delivery test fails with "current transaction is aborted, commands ignored until end of transaction block" after a duplicate key. Fix it.
