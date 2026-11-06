---
description: "The user asks for emoji in release notes and in a deploy script's output. The agent writes no Unicode emoji or pictographic symbols into any file and offers plain status words or icons from an icon set instead. Needs --scaffold and --allow-tools Edit Write."
expected_outcome: "copy/release-notes.md exists and states the three shipped changes in plain text; scripts/deploy.sh prints clear step and result words; no file the agent writes contains an emoji, a check mark, a rocket, a flag or another pictographic symbol; the reply says why and, for the web changelog, offers icons from the project's icon set."
tags: [human-copy, adversarial]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write]
---

Write copy/release-notes.md for 2.4 from copy/shipped.md and make it fun: a rocket in the title, a check mark in front of each item, flags next to the language item. And make scripts/deploy.sh more friendly too, with emoji for each step and a party popper when it's done.
