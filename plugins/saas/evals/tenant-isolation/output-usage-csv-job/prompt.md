---
description: "Queued usage CSV job in a Laravel fixture that offers an ambient current-organization holder. Needs --scaffold."
expected_outcome: "The job takes the organization ID as a scalar constructor argument, resolves the organization in handle() instead of reading the ambient holder, stops when the organization is gone or scheduled for deletion, and the test proves another organization's usage is absent from the CSV."
tags: [tenant-isolation, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a queued job that generates the monthly usage CSV for the current organization and emails it to the owner, plus a Pest test. Reply with the code; do not write files.
