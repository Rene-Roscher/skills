---
type: llm
weight: 3
---

PASS if the cache key (or a tag) contains both the workspace and something derived from the member's visible project set or role set (for example a hash of the sorted visible project IDs), so that two members with different visibility never share an entry, and the reply invalidates the entry when tasks change.
FAIL if the key holds only the workspace, so one member's numbers can be served to another, or if nothing invalidates the entry on writes.
