---
description: "Containerize a Nuxt project-tool front end with a .env file and a git directory in the context. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "A multi-stage Dockerfile with digest-pinned bases, npm ci, a numeric non-root USER and an exec-form entrypoint, plus a .dockerignore that excludes .env and .git, and no secret-named ARG or ENV."
tags: [container-images, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Containerize this Nuxt app for production.
