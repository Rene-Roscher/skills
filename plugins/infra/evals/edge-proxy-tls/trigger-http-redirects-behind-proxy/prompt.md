---
description: Should load edge-proxy-tls. Train split. Run with --ablation none --threshold 0.5.
tags: [edge-proxy-tls, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Behind our Caddy edge and an nginx ingress, the app generates http:// redirects and canonical URLs although the site is served over https. Where should we fix this?
