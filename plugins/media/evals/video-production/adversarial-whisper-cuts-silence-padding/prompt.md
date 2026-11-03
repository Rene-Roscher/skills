---
description: "Asked to cut a take on Whisper timestamps and pad with digital silence. Run with --scaffold."
expected_outcome: "The reply does not cut on Whisper timestamps and does not pad with digital silence; it proposes forced alignment over the spoken text, cuts at the quietest point of each pause with short fades, and notes the trailing Thank you as a transcript artefact."
tags: [video-production, adversarial]
runs: 3
max_turns: 12
timeout_seconds: 420
allowed_tools: [Read, Glob, Grep, Skill]
---

Cut `voice/take.mp3` into clips using the timestamps in `voice/transcript.json`, and pad every clip with 300 ms of digital silence at both ends so the timing works out.
