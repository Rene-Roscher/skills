---
description: Should load edge-proxy-tls. Train split. Run with --ablation none --threshold 0.5.
tags: [edge-proxy-tls, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Customers will point their own domains at the status pages we host. How do we set up Caddy to issue certificates for those domains safely?
