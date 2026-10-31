---
description: Should trigger. Mailer selection at the call site. Run with --ablation none.
tags: [laravel-production-runtime, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

In Laravel 12, the receipt mail went out through the marketing SMTP mailer instead of the transactional one, although the mailable sets its mailer.
