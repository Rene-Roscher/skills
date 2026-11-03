---
description: "Should trigger vue-inertia-frontend (validation split). Run with --ablation none."
tags: [vue-inertia-frontend, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Make the incidents list page refresh every 30 seconds without reloading all of its page props.
