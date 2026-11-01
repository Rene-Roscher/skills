---
type: llm
weight: 2
---

PASS if the final reply explains that by default Claude Code reads AGENTS.md only when there is no CLAUDE.md in the working directory or above, so the table in AGENTS.md was never loaded, and that the fix is an import line in CLAUDE.md. FAIL if it blames something else or does not explain.
