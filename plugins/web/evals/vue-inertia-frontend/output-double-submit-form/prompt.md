---
description: "An Inertia Form with a submit listener, typeless buttons and a keyup.enter submit; the fix removes all three causes of duplicate requests. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Removes @submit from the Form and gates through onBefore, gives Cancel type=button and Create type=submit disabled while processing, removes the keyup.enter handler, and explains each cause.
tags: [vue-inertia-frontend, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Users get two projects when they click Create once. Fix resources/js/pages/Projects/Create.vue.
