---
description: "Should trigger video-production. Run with --ablation none."
tags: [video-production, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Generate the voice-over for the approved script with ElevenLabs and cut the take into one clip per line.
