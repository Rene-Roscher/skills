---
description: SMS integration that may change providers needs an interface, a fake, an architecture test and spend caps. Run with --scaffold.
expected_outcome: The reply defines an own SMS interface, a fake implementing it, an architecture test that confines the vendor SDK, and per-recipient or per-tenant caps or a breaker.
tags: [build-vs-buy, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Integrate an SMS provider for appointment reminders in this booking app. We may switch providers later. Answer with the code you would add, including tests.
