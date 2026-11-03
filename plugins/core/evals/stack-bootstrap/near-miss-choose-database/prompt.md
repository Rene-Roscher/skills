---
description: "Near miss for stack-bootstrap (train split): choosing a datastore. Run with --ablation none."
tags: [stack-bootstrap, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Should the new analytics feature store its events in ClickHouse or in PostgreSQL?
