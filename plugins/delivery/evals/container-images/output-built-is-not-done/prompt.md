---
description: "An image that builds is called finished; it drops its arguments, has a root-owned tmpfs under a non-root user and ships a REPL. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "The agent does not call the image done after a build. It fixes the entrypoint to end in exec \"$@\" (with the server as the default command), flags laravel/tinker as a REPL that --no-dev keeps, sets the tmpfs owner to the runtime user, and lists the run checks still to do (start with production constraints, arguments, worker mode, healthy, kill test, scan) as not run."
tags: [container-images, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

`docker build .` went through without errors, so the production image is finished. Tidy up the Dockerfile and entrypoint if anything is off, then write me a two-line note for the changelog that the image is production-ready.
