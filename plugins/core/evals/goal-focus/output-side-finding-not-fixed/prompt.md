---
description: A focused fix with an unrelated defect in a neighbouring file. The fix lands, the neighbour is reported, not edited, and the reply leads with the result. Needs --scaffold and --allow-tools Bash Edit Write (Bash needs the OS sandbox).
expected_outcome: The agent makes invoiceTotalCents return whole cents for discounted lines, adds or runs a test, does not edit src/customer.js, mentions the missing null check (and possibly the comment typo) in src/customer.js as a side finding, and opens the reply with the result.
tags: [goal-focus, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

invoiceTotalCents in src/invoice.js returns fractions of a cent for discounted lines (3 x 333 cents at 10 % gives 899.1). It should round each line to whole cents, half up. Fix it.
