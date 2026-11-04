---
description: "Pre-deploy check of a built static site with three planted issues: noindex left on the pricing page, robots.txt disallowing OAI-SearchBot and Claude-SearchBot for the whole site, and Organization review stars on the integrations page. The skill's fast path must run site_check.py on the build and copy its findings. Needs --scaffold and --allow-tools Bash."
expected_outcome: "The agent runs site_check.py with --root-dir dist and --base-url https://www.example.com, reports that it exited 1, and lists the noindex blocker, the robots.txt block of the two AI search agents and the self-serving review markup in the finding format (severity, URL, Evidence, Fix, Verify) as the script printed them. It states no ranking or traffic figures and leaves the decision to keep or lift the AI-agent block to the owner."
tags: [search-visibility, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Our marketing build is in dist/ and goes live at https://www.example.com tonight. Check it for search and AI visibility problems first and give me the findings.
