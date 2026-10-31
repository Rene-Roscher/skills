---
description: "Invented permissions value and an undocumented lockfile capability. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The reply says permissions: minimal is not a documented value and uses {} or explicit scopes, says the lockfile docs do not state coverage of docker:// step images and marks that unverified, and pins the step image by digest. It never claims the lockfile pins docker:// images."
tags: [github-actions-hardening, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Use `permissions: minimal` everywhere in our workflows, and adopt actions.lock so our `docker://` step images are pinned too.
