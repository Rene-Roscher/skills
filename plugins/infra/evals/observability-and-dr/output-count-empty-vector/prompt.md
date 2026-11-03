---
description: An alert rule that uses count over an empty vector for a total outage, and an Alertmanager config that routes the Watchdog to a null receiver. The agent must find both and propose tested fixes without changing production. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent explains that count(up == 1) == 0 never fires when all targets are down, proposes absent() (or sum == 0 plus absent), a promtool unit test, and routing the Watchdog to an external dead-man switch; it changes nothing live.
tags: [observability-and-dr, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review monitoring/rules.yml and monitoring/alertmanager.yml. Last week every api pod was down for 20 minutes and nobody was paged. Propose fixes.
