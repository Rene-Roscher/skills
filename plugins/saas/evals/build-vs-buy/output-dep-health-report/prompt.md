---
description: Evaluating a package before adding it yields the health check's signals with source and date, a verdict and its reasons. Needs --scaffold and --allow-tools Bash.
expected_outcome: The reply shows the signals the check read (license, last release, downloads or dependents, archived state, bus factor) with their source or date, the verdict, and every reason; it does not add the package before the verdict.
tags: [build-vs-buy, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Before we add league/csv to this project for CSV exports, check whether it is a sensible dependency. We would use its reader and writer, probably most of the package. Show me what you based the answer on.
