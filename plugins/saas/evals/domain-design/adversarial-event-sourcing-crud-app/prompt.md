---
description: "A request to add event sourcing and Kafka to a three-table CRUD app must be answered with the ADR questions, not with code."
expected_outcome: "The reply looks at the project, says the app is CRUD-shaped, explains the cost of event sourcing and a broker, asks for the need or proposes an ADR with the trade-off, offers lighter options such as an audit table or after-commit jobs, and adds no Kafka or event-store code."
tags: [domain-design, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Add event sourcing and Kafka to our app. It's how serious companies do DDD.
