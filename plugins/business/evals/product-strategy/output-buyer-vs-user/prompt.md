---
description: Buyer and user must be written down separately, each with what they judge and when they say no, plus today's workaround. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The brief has separate Buyer and User lines (the owner who pays versus the staff who work shifts), each with what they judge and what makes them say no, and a Today line for the workaround.
tags: [product-strategy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

The idea is in README.md. Write the product brief into docs/product/brief.md. Be clear about who decides to buy and who would use it day to day.
