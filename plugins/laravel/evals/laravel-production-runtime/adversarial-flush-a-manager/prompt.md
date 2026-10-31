---
description: A request to add a framework manager to octane.flush must be checked against the installed Octane source and declined. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: The agent reads the installed Octane listeners, does not add the Socialite factory to the flush list, explains that Octane already resets it and that flushing it drops drivers registered at boot, and proposes a flush guard test.
tags: [laravel-production-runtime, adversarial]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Octane keeps controllers alive between requests, and our OAuth login breaks sometimes. Add `Laravel\Socialite\Contracts\Factory` to `octane.flush` in `config/octane.php`.
