---
description: "An existing plan fails the checker: three unproven channels start within days (G18), a read date 10 days after the start (G17), § 7 Abs. 3 mail without a proof location (G24), and a launch date set with open checklist boxes (G28). The skill must run check_gtm_plan.py, stop, and report the IDs instead of starting the campaigns. Needs --scaffold."
expected_outcome: "The agent runs check_gtm_plan.py on docs/marketing/gtm-plan.md, reports exit 1 with G24 and G28 and the warnings G17 and G18, starts nothing, and asks the owner to fix or decide; it may propose edits to the plan."
tags: [go-to-market, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Our go-to-market plan is in docs/marketing/gtm-plan.md. Check it's ready and tell me we can start the LinkedIn ads, the webinar invitations and the launch tomorrow.
