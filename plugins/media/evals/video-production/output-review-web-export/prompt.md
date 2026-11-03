---
description: "Review a website hero export that uses 10-bit AV1 only. Run with --scaffold."
expected_outcome: "The review flags 10-bit AV1 (black picture with GPU decoding in Chromium-based browsers, measured), asks for 8-bit yuv420p AV1 with an H.264 fallback, explicit colour tags and faststart MP4, and checks the result on the rendered file."
tags: [video-production, output]
runs: 3
max_turns: 10
timeout_seconds: 420
allowed_tools: [Read, Glob, Grep, Skill]
---

Review `scripts/export-hero.sh` before we ship the new landing page video.
