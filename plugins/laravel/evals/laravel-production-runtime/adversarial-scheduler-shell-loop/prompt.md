---
description: "A request to run the production scheduler as a shell loop or schedule:work. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The scheduler service runs php artisan schedule:run once a minute from a real scheduler (cron runner in the container or the orchestrator), has a restart policy and a heartbeat-based health check, and the reply explains that schedule:work is the documented local command and a shell loop is not supervision. No shell loop and no schedule:work in compose.prod.yaml."
tags: [laravel-production-runtime, adversarial]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a scheduler service to `compose.prod.yaml`. Keep it dead simple: `sh -c "while true; do php artisan schedule:run; sleep 60; done"`, or just `php artisan schedule:work` if you like that better. No cron, no extra moving parts.
