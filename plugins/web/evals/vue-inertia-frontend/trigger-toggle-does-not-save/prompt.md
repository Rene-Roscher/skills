---
description: "Should trigger vue-inertia-frontend (train split). Run with --ablation none."
tags: [vue-inertia-frontend, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The notification toggle in resources/js/pages/Settings.vue moves when clicked, but the saved value never changes.
