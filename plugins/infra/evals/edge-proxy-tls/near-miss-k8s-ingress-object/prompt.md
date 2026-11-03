---
description: Must not load edge-proxy-tls. Train split. Run with --ablation none --threshold 0.5.
tags: [edge-proxy-tls, near-miss]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a Kubernetes Ingress for our api service with host api.example.com and a cert-manager issuer annotation.
