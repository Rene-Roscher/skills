---
description: Must not load localization; storage of timestamps is a database concern. Validation split. Run with --ablation none --threshold 0.5.
tags: [localization, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our PostgreSQL columns store booking times as timestamp without time zone. Write a migration that converts them to timestamptz, assuming the old values were UTC.
