---
description: "A multi-step checkout across modules must get an orchestrated flow with stored state, deadlines and compensation."
expected_outcome: "The reply proposes a process manager or orchestrator with stored per-flow state, gives each step a deadline or timeout, names compensating actions such as releasing the hold or refunding, and keeps the confirmation mail as a simple reaction."
tags: [domain-design, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Booking checkout: hold a room, charge the card, confirm the booking, email the guest. These live in our Availability, Payments, Booking and Notifications modules. Design how the steps run and what happens when one fails. No code yet.
