---
type: llm
weight: 3
---

PASS if either holds:
(a) the reply reports a contrast ratio for the muted text in dark mode measured in a headless browser, states how dark mode was set (the page's own `theme` value in localStorage, or an explicit note that it was emulated), compares the ratio with 4.5:1, concludes that the text fails (the dark-mode pair measures about 3:1), and names an element screenshot path; or
(b) the reply says no browser could run, says the result is not verified in a browser, and labels any ratio it gives as computed from the CSS source rather than measured.
FAIL if the reply calls the text readable or unreadable without a number, or claims a browser measurement that the transcript does not show.
