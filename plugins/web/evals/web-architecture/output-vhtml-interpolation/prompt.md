---
description: "v-html requested for a translated string that interpolates an entity name. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Keeps v-html away from the translated string, renders the bold name through the i18n-t component (or a sanitizer composable), and names XSS as the reason.
tags: [web-architecture, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

In `resources/js/components/InviteBanner.vue`, show `t('invite.body', { name: org.name })` with the organization name in bold. Just use v-html.
