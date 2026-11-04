---
description: "A request for Billing to query the Orders table directly must be redirected to the owner's public surface, the context map and the arch test."
expected_outcome: "The reply reads the context map and arch test, declines the direct table read, proposes a query interface owned by Orders, an event-fed copy or a published view, updates the context map and arch rule for the new edge, and flags the new edge as an owner decision if it is not in the map."
tags: [domain-design, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Quick one: have the Billing module read the orders table directly with DB::table('orders') so invoices can show order totals. It's the same database anyway.
