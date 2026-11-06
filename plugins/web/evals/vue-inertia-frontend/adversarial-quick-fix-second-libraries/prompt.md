---
description: "A quick fix phrased so moment and a second toast library look fastest, in an app that already has date-fns and vue-sonner. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Keeps the favorites already installed (vue-sonner through the existing wrapper, Intl.RelativeTimeFormat or date-fns for the relative time), adds neither moment nor vue-toastification, and says briefly why one library per need is kept.
tags: [vue-inertia-frontend, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Quick fix for `resources/js/pages/projects/Edit.vue`: after saving, show "Saved 3 hours ago" style text next to the button and pop a success toast. Just add moment.js and vue-toastification to package.json, that's what I know and it's fastest. Don't overthink it.
