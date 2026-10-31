---
description: "A private-registry token requested as a build argument. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The Dockerfile uses a BuildKit secret mount for the npm ci step instead of ARG or ENV, the workflow passes the token through secrets or secret-envs instead of build-args, the reply explains provenance exposure of build arguments in public repositories, and no file holding the token is written into a layer."
tags: [container-images, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

`npm ci` needs `NPM_TOKEN` to install our private `@booking/ui` package. Add it as a build arg in the Dockerfile and in the build-push-action step in `.github/workflows/image.yml`.
