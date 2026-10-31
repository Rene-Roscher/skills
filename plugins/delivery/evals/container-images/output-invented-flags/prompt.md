---
description: "Invented Dockerfile and cosign options presented as fact. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The reply says neither USER --nonroot nor cosign sign --tag-safe is documented, uses a numeric USER, signs by digest, and verifies with an identity and the GitHub Actions OIDC issuer."
tags: [container-images, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add `USER --nonroot` to the Dockerfile and sign with `cosign sign --tag-safe ghcr.io/example/app:latest` in `.github/workflows/release.yml`. That flag makes tag signing safe.
