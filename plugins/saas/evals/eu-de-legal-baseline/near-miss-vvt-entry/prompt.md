---
description: "Near miss: must not trigger eu-de-legal-baseline (train split). Run with --ablation none."
expected_outcome: "The eu-de-legal-baseline skill is not invoked."
tags: [eu-de-legal-baseline, near-miss]
runs: 3
max_turns: 5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add an entry to our record of processing activities (VVT) for the new support-ticket attachments feature: purpose, data categories, retention.
