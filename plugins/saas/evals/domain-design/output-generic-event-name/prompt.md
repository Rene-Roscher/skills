---
description: "A generic BookingUpdated event with the whole row as payload must become specific past-tense events published after commit."
expected_outcome: "The reply rejects BookingUpdated as too generic, proposes specific past-tense events for the business changes (for example BookingRescheduled), keeps the payload to facts consumers need, publishes after commit or through an outbox, and makes the Invoicing consumer idempotent."
tags: [domain-design, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a BookingUpdated event that fires whenever anything on a booking changes, with the whole booking row as payload, so Invoicing can re-price. Just describe the design, no code yet.
