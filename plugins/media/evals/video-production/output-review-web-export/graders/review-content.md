---
type: llm
weight: 3
---

PASS if the review flags the 10-bit AV1 output as a risk of a black picture in browsers that decode on the GPU, recommends 8-bit 4:2:0 AV1 plus an H.264 fallback for browsers without AV1, asks for the colour matrix to be tagged, and says the check must be done on the exported file in real browsers rather than only headless.
FAIL if it approves the script as is, or recommends 10-bit for quality without naming the black-picture risk.
