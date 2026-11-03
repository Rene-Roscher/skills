---
description: Should load edge-proxy-tls. Validation split. Run with --ablation none --threshold 0.5.
tags: [edge-proxy-tls, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Caddy edge runs as root with network_mode host in docker compose. How should we harden it, and how do we check config changes in CI?
