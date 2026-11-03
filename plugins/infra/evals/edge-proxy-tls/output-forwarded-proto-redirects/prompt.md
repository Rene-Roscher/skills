---
description: Caddy forwards to an in-cluster nginx ingress, which forwards to an app that trusts every proxy. Redirects come out as http with port 80. The agent must locate the hop that loses the scheme and propose a fix without applying. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent explains that the ingress hop reports http and port 80, proposes passing the edge headers through only from the edge range or deriving the scheme from the base URL, absolute_redirect off, and a curl -sI check of Location; it does not recommend trusting all proxies.
tags: [edge-proxy-tls, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Our redirects come out as http://shop.example.com:80/... although everything is https at the edge. Look at deploy/ and tell me what to change and how to verify it.
