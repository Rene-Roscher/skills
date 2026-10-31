---
description: A request for inline validation gets a FormRequest that follows the existing convention, and the reply says why. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: A new FormRequest holds the rules, the controller calls no validate method, and the reply names the FormRequest convention or the ADR route for inline validation.
tags: [laravel-architecture, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Quickly add validation for `customer_reference` (required, max 64 characters) and `amount_cents` (required integer, at least 1) in `InvoiceController@update`. Just inline is fine.
