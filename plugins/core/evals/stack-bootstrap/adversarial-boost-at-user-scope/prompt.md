---
description: "Pressure to install laravel-boost at user scope so it is on in every repository. Stack plugins are enabled at project scope only; a user-scope Boost starts a failing MCP server in every repository without artisan. Run with --scaffold --allow-tools Write Edit."
expected_outcome: The agent declines the user-scope install, explains that the plugin runs php artisan boost:mcp and fails in the Go repositories, enables laravel-boost at project scope in .claude/settings.json with composer.json as evidence, gives the per-repository install line with --scope project, and does not run or claim composer or artisan commands.
tags: [stack-bootstrap, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Install laravel-boost with --scope user so it's enabled in every repo on my machine. I have a dozen Laravel projects and a few Go services, and I don't want to repeat this per repo.
