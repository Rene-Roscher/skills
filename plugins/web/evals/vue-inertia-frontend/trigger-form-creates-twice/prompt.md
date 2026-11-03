---
description: "Should trigger vue-inertia-frontend (train split). Run with --ablation none."
tags: [vue-inertia-frontend, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

The create-project form on our Inertia page sometimes creates two projects per click. Fix resources/js/pages/Projects/Create.vue.
