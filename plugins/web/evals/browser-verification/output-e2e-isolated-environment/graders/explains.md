---
type: llm
weight: 3
---

PASS if the reply explains both causes (the rate-limit counter persists in the database cache between runs; the suite reuses the dev server and dev database) and the fix: its own port and database, a global setup that resets the database and clears the cache, and a limit read from the environment with a test value, while the production limit stays.
FAIL if the reply removes or raises the production throttle as the fix, adds retries or waits, or keeps running against the dev server and dev database.
