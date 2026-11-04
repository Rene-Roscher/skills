---
description: "A server list with '1 Server(s)', a count glued to a translated fragment, a raw exception in a flash and a toast, and a concatenated count in the controller must be reviewed for localization. Needs --scaffold."
expected_outcome: The agent reads the page, the locale files and the controller, and flags the pseudo-plurals, the count concatenated with a fragment, the hard-coded button text and status message, and the raw exception messages; it proposes one plural message per count (vue-i18n with the count, trans_choice in Laravel), a zero text, and error codes or translated keys instead of exception text.
tags: [localization, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Review resources/js/pages/Servers/Index.vue, its locale files and app/Http/Controllers/ServerController.php for localization problems. We ship German and English. List what is wrong and show the fixed messages.
