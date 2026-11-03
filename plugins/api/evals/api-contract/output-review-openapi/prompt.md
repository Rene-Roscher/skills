---
description: An OpenAPI document with integer IDs, unbounded offset lists, ad-hoc errors and no idempotency on create must be flagged. Needs --scaffold.
expected_outcome: The agent reads openapi.yaml and reports integer IDs, the missing maximum page size or cursor, the non-standard error shape, and the missing Idempotency-Key on POST, and says it is not ready.
tags: [api-contract, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Review openapi.yaml for our first public API release. Is it ready?
