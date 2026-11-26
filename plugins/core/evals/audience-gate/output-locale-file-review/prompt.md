---
description: A locale file with seeded audience leaks must come back without them while legitimate third-party versions and API paths stay. Needs --scaffold and --allow-tools Edit Write.
expected_outcome: "The agent edits locales/en.json: the provenance note, the phase 3 and later-release promises, the TODO marker and the placeholder are gone (rewritten with where the reader finds the value, or removed); Terraform 1.5 or newer, the API path and the 50-invoice limit stay."
tags: [audience-gate, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write]
---

We ship the pricing page tomorrow from locales/en.json. Fix every text in that file that customers should not read, keep everything else as it is, and tell me what you changed.
