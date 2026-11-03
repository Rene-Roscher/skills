---
description: Should load edge-proxy-tls. Validation split. Run with --ablation none --threshold 0.5.
tags: [edge-proxy-tls, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this part of our Caddyfile: on_demand_tls { ask http://app:8080/caddy/check?secret=abc123 interval 2m burst 5 }
