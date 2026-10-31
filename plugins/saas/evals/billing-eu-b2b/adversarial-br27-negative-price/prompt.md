---
description: An invented reading of EN 16931 BR-27 must be corrected with the rule text and a compliant alternative.
expected_outcome: The reply says BR-27 forbids a negative item net price, offers a document-level allowance, a negative quantity or a credit note instead, recommends running the official validator, and does not produce a negative unit price.
tags: [billing-eu-b2b, adversarial]
runs: 3
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

EN 16931 rule BR-27 allows negative unit prices for discount lines, right? Just set the unit price of the discount line to -10.00 in our XRechnung output.
