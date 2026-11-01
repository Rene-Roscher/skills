---
description: A count and a sum over a JSON file are computed with a query tool, without reading the file into context. Needs --scaffold and --allow-tools Bash.
expected_outcome: The agent runs a jq (or equivalent scripted) query over data/orders.json, reports 24 refunded orders totalling 150000 cents, and does not open the file with the Read tool.
tags: [agent-toolbelt, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

How many orders in data/orders.json have status refunded, and what is their total amount in cents? Do not print the file.
