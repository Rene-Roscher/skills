---
description: "Must not invoke github-actions-hardening (validation split). Run with --ablation none."
expected_outcome: "The github-actions-hardening skill is not invoked."
tags: [github-actions-hardening, near-miss]
runs: 3
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a Terraform module for an S3 bucket with versioning enabled.
