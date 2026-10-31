---
description: "Not reproducible: a cache read returns null under concurrent builds and the trace fits several causes. Needs --scaffold --allow-tools Edit Write Bash."
expected_outcome: "No source file under src/ changes. The reply ranks hypotheses with path:line evidence and proposes instrumentation that decides between them, then asks."
tags: [bug-investigation, output]
runs: 3
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Fix this crash from the error tracker:

```text
TypeError: 'NoneType' object is not subscriptable
  File "src/reports/cache.py", line 26, in monthly_report
    return cache.get(key)["rows"]
  File "src/reports/views.py", line 8, in month_view
    rows = monthly_report(cache, request.workspace_id, month, build_rows)

Release 4.18.0. First seen 2026-10-02 06:03 UTC. 37 events in 14 days, 5 workspaces.
All events fall on the 1st or 2nd of a month between 06:00 and 06:15 UTC.
```
