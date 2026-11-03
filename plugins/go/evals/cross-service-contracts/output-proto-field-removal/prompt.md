---
description: "Removing a protobuf field that a fleet still decodes. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The field is deleted, its number and name are reserved, no other field number changes, and the reply covers buf breaking and the order in which consumers and producers ship."
tags: [cross-service-contracts, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

We no longer need `legacy_code` in `CheckResult`. Remove it from `proto/worker/v1/result.proto`.
