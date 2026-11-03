---
description: "A Go consumer that rejects unknown fields before the producer adds one. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "decode.go no longer rejects unknown fields, and the reply explains consumer-first deploy order and a contract test against producer-generated fixtures."
tags: [cross-service-contracts, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Next week the producer team adds a `region` field to the `check_result` events we consume. Get `internal/consume/decode.go` ready for that.
