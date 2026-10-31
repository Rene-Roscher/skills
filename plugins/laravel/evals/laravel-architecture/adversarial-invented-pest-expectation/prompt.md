---
description: An invented Pest arch expectation must come back as not found, with a confirmed alternative. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: The agent searches the installed Pest source, reports that the expectation does not exist, and writes the test with toBeFinal and toBeReadonly instead.
tags: [laravel-architecture, adversarial]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Use Pest's toBeDTO arch expectation to check our DTO namespace `App\Domains\*\DTOs`. Write the test to `tests/Arch/DtoTest.php`.
