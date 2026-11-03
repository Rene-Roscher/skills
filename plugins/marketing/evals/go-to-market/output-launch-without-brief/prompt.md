---
description: "Launch plan requested in a repository with prices but no product brief (buyer, alternatives, positioning) and no attribution. The skill must stop on the missing positioning, route to product-strategy, and require attribution and a cost per paying customer target instead of upvote goals. Run with --scaffold."
expected_outcome: "The reply names the missing product brief and routes to product-strategy before writing launch messaging, asks for or proposes attribution of sign-ups to paying customers, and sets the launch goal as paying customers or cost per paying customer, not upvotes or visits."
tags: [go-to-market, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

We launch our booking tool for physiotherapy practices on a launch platform next Tuesday. Write the launch plan; the goal is to hit the top 5 of the day.
