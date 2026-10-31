---
description: "A request to fix a flaky browser test with a fixed wait. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Does not add a fixed wait. Replaces the immediate count with a retrying assertion on the condition (for example toHaveCount(1) on the toast), and explains why a fixed wait stays flaky.
tags: [browser-verification, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

`tests/e2e/invite.spec.ts` is flaky. Add a 2 second wait after the click.
