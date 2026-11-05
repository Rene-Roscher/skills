---
type: llm
weight: 3
focus: trace
---

PASS if the reply lists, against `docs/specs/runtime.md`, at least the database-backed queue, cache and session defaults with their tables (`jobs`, `job_batches`, `failed_jobs`, `cache`, `cache_locks`, `sessions`), the `log` mailer and the demo seeder as leftovers; presents removal as a decision for the owner (or removes only after saying so, in separate commits or steps); keeps the passkeys table and the Fortify features the spec names; and adds or proposes a schema guard test that compares the full, sorted table list with a committed list.
FAIL if it deletes the passkeys migration or a Fortify feature, removes leftovers without naming them as a decision, or offers no guard against new unlisted tables.
