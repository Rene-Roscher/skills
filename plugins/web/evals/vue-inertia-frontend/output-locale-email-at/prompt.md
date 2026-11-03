---
description: "Adding an email address to a vue-i18n locale file; the at sign is written as literal interpolation. Run with --scaffold --allow-tools Write Edit."
expected_outcome: Adds support.contact with the at sign written as {'@'} and the file stays valid JSON; mentions that a raw @ is message syntax in vue-i18n.
tags: [vue-inertia-frontend, output]
runs: 3
max_turns: 8
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add the key support.contact with the text "Write to support@example.com" to resources/js/locales/en/support.json.
