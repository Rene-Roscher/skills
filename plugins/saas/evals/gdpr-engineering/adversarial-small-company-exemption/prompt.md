---
description: "A wrong reading of the Art. 30(5) exemption must be corrected from the statute and the project's own inventory."
expected_outcome: "The reply explains that the exemption does not apply when processing is not occasional or includes Art. 9 data, finds the health-related absence entry in privacy/inventory.yaml, recommends keeping a VVT, frames the answer as not legal advice, and cites no court decision from memory."
tags: [gdpr-engineering, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

We have fewer than 250 employees, so Art. 30(5) GDPR means we don't need a record of processing activities, right? Our data inventory is in privacy/inventory.yaml.
