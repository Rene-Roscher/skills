---
type: llm
weight: 3
---

PASS if pointerdown reads the offset currently on screen (computed translate or transform), freezes the element there by stopping the transition in the same handler, and starts the drag origin so the first move continues from that offset; the reply names a test that presses the card shortly after release and checks that it does not move.
FAIL if the fix shortens or removes the spring-back, blocks pointer events while the card animates, waits for transitionend, or still starts the drag at zero.
