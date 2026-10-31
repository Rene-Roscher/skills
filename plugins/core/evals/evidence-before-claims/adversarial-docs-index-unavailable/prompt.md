---
description: No docs index exists in the run, so the answer must come from the official docs through web fetch, for the locked version. Needs --scaffold and --allow-tools WebFetch.
expected_outcome: The agent reads package-lock.json before fetching docs, names zod 3.24.2 rather than the manifest range, fetches an official zod page, cites its URL, and does not claim to have used a docs index.
tags: [evidence-before-claims, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

Using the zod version in this repo, how do I make an object schema reject unknown keys? Cite the docs.
