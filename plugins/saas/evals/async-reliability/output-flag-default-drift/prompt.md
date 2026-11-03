---
description: A feature switch whose default lives in two places, one of them wrong, must be traced to the duplicated default. Needs --scaffold.
expected_outcome: The agent reads the settings code and names the shared-props builder that hard-codes False as the cause, and proposes one accessor used by every reader plus a test that reads the real output.
tags: [async-reliability, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Last week we made booking reminders on by default. Customers still see the reminders toggle as off in the app, but reminders do get sent. Find the cause in this repo.
