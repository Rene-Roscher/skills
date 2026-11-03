---
description: "Should trigger tenancy-model (train split). Run with --ablation none."
tags: [tenancy-model, trigger]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our users table has a company_id column. Customers now want one login for several companies with different roles in each. How should we restructure this?
