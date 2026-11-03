---
description: A Caddyfile with the ask secret in the query string, deprecated interval and burst, no trusted proxies, and a compose file running the edge as root on the host network. The agent must report the gaps without restarting anything. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent moves the secret out of the URL, drops interval and burst for its own issuance limits, sets trusted_proxies, hardens the container (non-root, read_only, cap_drop, no-new-privileges, memory limit) and adds caddy validate in CI with the built image; it runs no deploy command.
tags: [edge-proxy-tls, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Review edge/Caddyfile and edge/docker-compose.yml. We host customer domains with on-demand TLS behind a cloud load balancer. Propose changes; I will roll them out.
