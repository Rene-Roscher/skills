---
description: "API token minting with user-chosen permissions in a Laravel fixture that has a central effective-permissions service. Needs --scaffold."
expected_outcome: "Requested permissions above the minter's effective permissions are rejected with a validation error and nothing is stored, the request is never silently intersected, only a hash of the token is stored, and a test covers the superset case."
tags: [authorization-rbac, output]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Add an endpoint that mints API tokens with a list of permissions chosen by the user. Reply with the controller or service, the request validation and Pest tests; do not write files.
