---
description: A term the owner explains must be added to docs/GLOSSARY.md so it is not asked twice. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent adds a Kasse row to docs/GLOSSARY.md with the five columns, a meaning that names the Mollie checkout page, and a not-to-confuse entry, and says in one line that it did.
tags: [glossary, output]
runs: 3
max_turns: 14
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

In this project "Kasse" is our Mollie checkout page, not the cash register module of the ERP. Make sure nobody has to ask me that again.
