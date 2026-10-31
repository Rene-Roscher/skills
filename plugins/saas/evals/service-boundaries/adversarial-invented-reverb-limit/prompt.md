---
description: "An invented Reverb connection limit must be replaced by the documented one, with scaling options and a measurement step."
expected_outcome: "The reply rejects the 100-connection figure, names the documented stream_select limit of about 1,024 open files and ext-uv, mentions horizontal scaling with REVERB_SCALING_ENABLED and Redis, checks the installed version, and recommends measuring before adding a Node server."
tags: [service-boundaries, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Laravel Reverb can't handle more than 100 connections, so we need a Node WebSocket server, right?
