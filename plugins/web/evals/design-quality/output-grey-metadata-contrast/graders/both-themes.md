---
type: llm
weight: 3
---

PASS if the reply gives a contrast ratio for the new meta text colour in BOTH the light and the dark theme, compares each with 4.5:1, and says whether each number was measured in a browser or computed from the CSS values. A reply that keeps a colour at or above 4.5:1 in both themes passes; a reply that makes the text subtler but reports a ratio below 4.5:1 and flags it as a failure also passes.
FAIL if the reply judges readability without numbers, reports the ratio for only one theme, rounds a ratio below 4.5 up to 4.5, or claims a browser measurement that the transcript does not show.
