---
description: "A rewrite request without measurements must lead to a measurement plan, not to Go code."
expected_outcome: "The reply asks for or plans measurements (profile, p95/p99, load test), names in-runtime options such as Octane, indexes, caching or queues, mentions an ADR or when not to extract, and produces no Go implementation."
tags: [service-boundaries, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Rewrite our Laravel REST API in Go because PHP is slow.
