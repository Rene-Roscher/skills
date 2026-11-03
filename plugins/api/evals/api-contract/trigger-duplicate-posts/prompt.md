---
description: Should load api-contract. Validation split. Run with --ablation none --threshold 0.5.
tags: [api-contract, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

API clients sometimes create duplicate bookings when their POST times out and they retry. Fix this in the API.
