---
description: A spec diff with a renamed field, a newly required parameter and one optional addition must be classified correctly. Needs --scaffold.
expected_outcome: The agent reads both specs and classifies the rename and the newly required parameter as breaking and the added optional field as compatible, and says it cannot ship as a minor release.
tags: [api-contract, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

spec-released.yaml is live; spec-next.yaml is what we want to release next. Can this go out as a minor release of v1?
