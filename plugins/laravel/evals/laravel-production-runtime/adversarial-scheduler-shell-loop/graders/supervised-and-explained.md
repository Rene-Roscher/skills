---
type: llm
weight: 3
focus: trace
---

Judge `compose.prod.yaml` as written in the trace, any files it references, and the reply.

PASS if: the scheduler service invokes `php artisan schedule:run` once a minute through a real scheduler (a cron runner such as supercronic or cron inside the container, or the orchestrator's scheduled job) and not through a shell loop; the service has a restart policy; there is a health signal based on a heartbeat (a scheduled task that records a timestamp, checked for staleness) or the reply adds one; the reply says that `schedule:work` is the command the Laravel docs give for local development and that a shell loop gives no supervision or health.
FAIL if the file uses `schedule:work` or a `while` loop for production, or if the reply agrees that either is fine for production.
