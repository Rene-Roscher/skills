---
type: llm
weight: 4
---

PASS if the reply (1) says every widget is computed inside one request, so the page is as slow as its slowest source and one failing API breaks or delays the whole page, (2) gives a per-view and per-day cost for the largest workspace with the facts given (40 users, 25 views per user per day, the paid reporting API price and free quota, the helpdesk rate limit), (3) proposes loading the expensive widgets independently with their own loading and error states, (4) proposes caching each expensive widget per workspace with a TTL based on how fresh the number must be, served stale while one refresh runs, or precomputing the revenue by month, and (5) names a cold and warm measurement (or marks its numbers as estimates with the command that would measure them).
FAIL if the reply calls the controller ready, if it only suggests adding an index or eager loading, or if it proposes caching without saying the key is per workspace.
