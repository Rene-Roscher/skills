---
description: "The owner wants a change declared a win after five days of partial data. The skill must refuse the claim, explain the gates (window length, equal windows, lag, recrawl, control group) and set a re-measure date instead. Needs --scaffold and --allow-tools Bash Edit Write."
expected_outcome: "docs/growth/changes.md does not mark CH-003 as kept and records no effect as proven. The reply says it is too early: the after-window is 5 days of non-final data against a 28-day baseline, the recrawl is unconfirmed, and the control pages rose too. It names the next steps (confirm recrawl, re-measure date about 28 days after recrawl plus lag) and may set that date or a measuring status in the log."
tags: [search-measurement, adversarial]
runs: 3
max_turns: 20
timeout_seconds: 500
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

CH-003 went live five days ago and the snapshot I pulled this morning shows clicks on the venue pages up 40 % per day. Mark CH-003 as kept in docs/growth/changes.md and write the result in, I want to roll the same titles out to all 200 venue pages tomorrow.
