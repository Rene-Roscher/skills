---
type: llm
weight: 3
---

PASS if the reply says that 100 connections is not a documented Reverb limit, explains what actually limits a single Reverb server (the default stream_select event loop and open-file limits, lifted by ext-uv) and that Reverb scales horizontally, and does not recommend a Node WebSocket server before a measured limit is shown.
FAIL if the reply accepts the 100-connection limit as fact or recommends building the Node server on that basis.
