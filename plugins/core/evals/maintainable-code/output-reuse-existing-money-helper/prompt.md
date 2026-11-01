---
description: A new total line must reuse the repository's existing money formatter instead of writing a second one. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent searches the repository, finds src/shared/money.py format_money, imports it in src/invoices/summary.py and adds no second formatter. It names the search in its reply.
tags: [maintainable-code, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

In src/invoices/summary.py, add a total line that shows the invoice total in euros with two decimals and a thousands separator.
