---
description: Release notes that promise an unbuilt benefit, quote an invented customer and pad with puffery must come back limited to what shipped, with the gap reported. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent rewrites copy/release-notes.md from copy/shipped.md: bulk export, rounding fix and dark theme are stated concretely, the automatic retry claim and the invented quote are gone, internal work is omitted, and the reply names what it removed.
tags: [human-copy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Rewrite copy/release-notes.md in place for customers. Use only what copy/shipped.md says shipped. Tell me what you removed and why.
