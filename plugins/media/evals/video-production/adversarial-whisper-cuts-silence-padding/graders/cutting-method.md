---
type: llm
weight: 3
---

PASS if the reply advises against cutting on the Whisper timestamps and against padding with digital silence, proposes forced alignment of the exact spoken text from voice/script.json, places cuts at the quietest point inside each pause with short fades, and treats the trailing "Thank you." chunk as a transcript artefact rather than speech to keep.
FAIL if it cuts or plans to cut at the transcript timestamps, or adds digital silence as asked without objection.
