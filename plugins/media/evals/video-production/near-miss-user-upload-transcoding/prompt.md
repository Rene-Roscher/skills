---
description: "Near miss for video-production: backend transcoding of user uploads. Run with --ablation none."
tags: [video-production, near-miss]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Users upload videos in our app. Add a backend job that transcodes them to HLS with three renditions.
