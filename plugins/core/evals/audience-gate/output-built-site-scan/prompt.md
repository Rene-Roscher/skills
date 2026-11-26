---
description: A static build with bytes after the closing html tag, a raw locale key in JSON-LD and a German description on an English page must be reported, ideally with the bundled scanner. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: "The agent scans dist/ (with audience_scan.py or by reading the files) and reports the bytes after </html> in index.html, the raw key nav.pricing in the breadcrumb, and the German organisation description on the English page."
tags: [audience-gate, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

dist/ is the production build of our marketing site. Before we deploy it, check what visitors and search engines will get.
