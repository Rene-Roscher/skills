---
description: An error tracker init that sends PII and captures local variables and request bodies, and a logger that prints all request headers. The agent must report each leak and propose config and a test. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent turns off default PII, local-variable capture and request bodies, adds a before_send scrubber, stops logging Authorization and cookies, and proposes a test that asserts a fake token never reaches the output.
tags: [observability-and-dr, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review app/telemetry.py for data that should not leave the service. Propose changes and a test.
