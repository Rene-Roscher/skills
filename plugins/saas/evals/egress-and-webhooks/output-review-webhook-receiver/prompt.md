---
description: An inbound webhook handler that verifies a re-serialized body with == and processes inline without dedup must be flagged. Needs --scaffold.
expected_outcome: The agent reads webhook.py and reports verification over re-encoded JSON instead of the raw body, the non constant-time compare, the missing timestamp check and the missing dedup.
tags: [egress-and-webhooks, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Review webhook.py, our receiver for signed events from a partner. Anything to fix before launch?
