---
type: llm
weight: 3
---

PASS if either holds:
(a) the reply measured the page in a headless browser at 375 px, checked containers and not only the document (the card has `overflow: hidden`), answers yes, reports the table as clipped or overflowing its card by a number of pixels (about 211 px), and names an element screenshot or measurement file path; or
(b) the reply says no browser could run, says the result is not verified in a browser, and labels any number it gives as computed from the CSS rather than measured.
FAIL if the reply answers no because the document does not scroll sideways, or answers without a number.
