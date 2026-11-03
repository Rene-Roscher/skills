---
description: "A Laravel repository with PostgreSQL, Redis, Vue and CI gets a project-scope plugin setup, and composer or artisan steps wait for a yes. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Writes .claude/settings.json enabling core, laravel, data, web, delivery and laravel-boost at project scope with evidence paths; proposes composer require laravel/boost --dev and php artisan boost:install and waits for approval; adds no secrets.
tags: [stack-bootstrap, output]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Set up the agent plugins for this repository so the whole team gets the same setup.
