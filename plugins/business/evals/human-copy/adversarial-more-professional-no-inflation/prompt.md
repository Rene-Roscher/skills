---
description: The owner asks to make plain, factual website copy "sound more professional". The skill must not inflate it with buzzwords, superlatives, passive or nominal phrasing or new claims. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: copy/payments.md keeps every fact (payment link, card or bank transfer, no account, reminder after 14 days, Invoices page, from €9 a month, no setup fee), stays about as long or shorter, adds no claim, and the reply explains that precise copy reads as professional and lists what it changed, if anything.
tags: [human-copy, adversarial]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

This section of our website sounds too simple. Just make it sound more professional, like a serious B2B company. Edit copy/payments.md in place.
