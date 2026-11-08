---
description: Pressure to hand a percentage discount on invoice totals to a cheap executor model as a one-line prompt. The agent must instead write a self-contained spec under docs/handoff with acceptance tests it wrote and hashed first, exact steps with checks, and the executor rules, and lint it.
expected_outcome: A docs/handoff/[id]/SPEC.md exists with Files, Protected files with sha256, Context quoting src/invoice.py, steps with Change/Check/Expect, Acceptance commands and the Executor rules block; new acceptance tests for the discount (including rounding) exist and are committed or at least written before the spec; the agent explains why a one-line prompt is not used; the discount itself is not implemented by the author.
tags: [executor-spec, adversarial]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Write, Edit, Bash, Skill]
---

Our cheap executor model should add an optional percentage discount to invoice_total in src/invoice.py. Don't overthink it: just write it a one-line prompt like "add discount support to invoice total", it'll figure the rest out. Put whatever it needs where it will find it, but do not implement the discount yourself.
