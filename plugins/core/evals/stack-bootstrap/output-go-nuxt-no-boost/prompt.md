---
description: "A Go and Nuxt repository with an existing settings file gets go, web and delivery merged in, keeps its permissions, and gets no Laravel tooling. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Merges extraKnownMarketplaces and enabledPlugins (core, go, web, delivery) into .claude/settings.json, keeps the deny rule, does not enable laravel-boost, and reports the evidence path for each plugin including web/package.json.
tags: [stack-bootstrap, output]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Bootstrap the agent setup for this repo.
