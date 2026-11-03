---
description: "Should trigger eu-de-legal-baseline (train split)."
expected_outcome: "The eu-de-legal-baseline skill is invoked."
tags: [eu-de-legal-baseline, trigger]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

We're adding an LLM chat assistant that drafts task descriptions inside our project tool, launching to EU customers next month. Besides the prompt engineering, what do we have to put in place before launch?
