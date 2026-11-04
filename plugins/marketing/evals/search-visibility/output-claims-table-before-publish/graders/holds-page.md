---
type: llm
weight: 4
focus: last_message
---

PASS if the reply says the page is not ready to publish and names all three failing rows with their reasons: (1) team members, where the page says 15 but the cited config line says 10, (2) the time-tracking interval, sourced from another marketing page (site/features.html) instead of code, config or a dated record, (3) the hosting location, which has no source. It says each failing claim is corrected, sourced or removed before the page goes live, and leaves the passing rows alone.
FAIL if the reply calls the page ready, misses any of the three rows, flags a passing row (price, projects, storage) as failing, or proposes changing the config to match the marketing copy.
