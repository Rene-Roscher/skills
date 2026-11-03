---
name: performance-gate
description: "Gates a feature with data or traffic impact before handover: query budget per request measured with a frozen clock, N+1, indexes tied to their query, EXPLAIN on the real engine, tagged cache invalidation, queue and broadcast fan-out, paid-message cost, worker memory, load at 100x tenant size, bulk paths. Use when handing over such a feature or asked whether it scales. Not for page-load speed."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Performance gate

This skill decides whether a feature that reads or writes data, sends messages or runs in background workers is
ready to hand over. It measures cost per request and per action, sizes it for the largest tenant times 100, and
reports findings in one fixed format. Engine details stay in `postgres-production` (data plugin) and
`laravel-production-runtime` (laravel plugin); this skill sets the gate and the evidence. The failure it prevents:
a feature that is fast with three seeded rows and falls over, or runs up a message bill, for the first large
tenant.

## Applies when / does not apply

- Applies: a new or changed list, detail page, API endpoint, export, import, report, scheduled job, queue job,
  broadcast, notification or webhook fan-out; a new index, cache or query; "is this performant", "will it scale",
  "N+1", "this is slow", a slow-transaction or N+1 alert from monitoring; the performance item of a definition of
  done.
- Does not apply: frontend bundle size and page-load metrics, image optimisation, build speed, choosing a
  database, writing migrations without a query change (`postgres-production`), the performance budget in a plan
  (`feature-planning` writes it; this gate measures against it).

## Rules

Most important first.

- [invariant] A finding has four parts: location (`path:line`), trigger (the input or action that causes it),
  magnitude (a measured number, or a formula with the volumes plugged in) and fix. A suspicion without a
  measurement is reported as "not measured" with the command that would measure it. Why: a list of hunches cannot
  be prioritised or checked. Test: every finding in the report matches the format in
  `references/finding-format.md`. Source: reproducible with the test above.
- [invariant] Every list, detail and API endpoint touched has a query budget asserted in a test: a fixed count
  that does not grow with the number of rows (N = 1 and N = 50 give the same count), and total query time below the
  budget. The test freezes the clock before the first request. Why: one query per row is the most common
  regression, and an unfrozen clock lets timestamp writes and cache expiry add queries when a second boundary
  passes, so the count flickers. Test: add a lazy relation access in the serializer; the budget test turns red.
  Source: Laravel query events `DB::listen` (https://laravel.com/docs/12.x/database#listening-for-query-events,
  verified 2026-11-03); flicker reproducible by a one-second sleep between two measured requests without a frozen
  clock.
- [invariant] N+1 detection runs everywhere data is shaped, not only in controllers: serializers and API
  resources, page props, broadcast payloads, mails, exports and jobs. In Laravel, lazy loading throws outside
  production. Why: the loop that issues one query per row is often in a resource or a mail template. Test: the
  budget test above covers each surface the change touches; `Model::preventLazyLoading(! app()->isProduction())`
  throws on a lazy access in the test suite. Source:
  https://laravel.com/docs/12.x/eloquent-relationships#preventing-lazy-loading (verified 2026-11-03).
- [invariant] Every new index names the query it serves, and the plan of that query on the production engine and
  major version shows the index in use at representative volume. Before adding one, check that no existing index
  already covers it as a left prefix, and that none of the new index's columns duplicate an existing index. Why:
  an index without a query costs every write and buys nothing; plans on a toy table do not predict plans on a
  large one. Test: `EXPLAIN (ANALYZE, BUFFERS)` on seeded data shows an index scan on the new index for the named
  query. Source: https://www.postgresql.org/docs/current/using-explain.html, "results on a toy-sized table cannot
  be assumed to apply to large tables" (verified 2026-11-03); index design rules in `postgres-production`.
- [invariant] `EXPLAIN ANALYZE` of a data-modifying statement runs inside `BEGIN … ROLLBACK`, never against
  production primary data. Why: `ANALYZE` executes the statement and its side effects. Test: the transcript of the
  plan shows the surrounding `ROLLBACK`. Source: https://www.postgresql.org/docs/current/using-explain.html
  (verified 2026-11-03).
- [invariant] Every cached value has a tenant-scoped key, a TTL and tags, and a named write path that invalidates
  it, proven by a test that writes and then reads the fresh value. The cache store in tests supports the same
  features as production. Why: a cache without a proven invalidation serves stale or foreign data; tags silently
  do not exist on some drivers. Test: update the record through its normal write path; the next read returns the
  new value without waiting for the TTL. Source: https://laravel.com/docs/12.x/cache#cache-tags, "Cache tags are
  not supported when using the `file`, `dynamodb`, or `database` cache drivers" (verified 2026-11-03).
- [invariant] Fan-out per action is a formula with a bound: jobs, broadcasts, notifications and webhooks per
  action as a function of recipients, subscribers or affected records, chunked so one job never holds all
  recipients, with payloads that carry IDs and the fields the receiver renders, not whole models with relations.
  Background polling counts too: requests per minute equal open clients times polls per minute. Why: a single
  click that fans out to every subscriber is the largest load a feature creates. Test: with a faked queue and
  broadcaster, an action on a tenant with 1,000 recipients pushes the number of jobs the formula predicts and no
  payload exceeds the size budget. Source: reproducible with the test above.
- [invariant] Paid messages (SMS, voice, paid API calls) have a cost per action: messages times unit price,
  computed for the largest tenant, deduplicated per recipient and event, capped where the product defines a quota,
  and never repeated by a job retry. Why: a retry or a missing dedupe turns into a bill and into duplicate wake-up
  calls. Test: run the action twice and force one job retry; the fake sender records exactly one message per
  recipient. Source: reproducible with the test above.
- [invariant] Code that runs in long-lived workers (application servers that keep the app in memory, queue
  workers, consumers) keeps no request or tenant data in static or singleton state and grows no static array.
  Memory measured over many iterations stays flat, and the workers have recycle limits set. Why: the process
  serves the next request or tenant with the leftover state, and a static array grows until the worker is killed.
  Test: run the handler 1,000 times in one process and compare memory after warm-up with memory at the end.
  Source: https://laravel.com/docs/12.x/octane#managing-memory-leaks, workers restart after 500 requests by
  default (`--max-requests`); queue workers `--max-jobs`, `--max-time`, `--memory`
  (https://laravel.com/docs/12.x/queues#running-the-queue-worker), both verified 2026-11-03.
- [invariant] Bulk paths never load a whole table or a whole tenant into memory: iterate by key in chunks, insert
  and update in batches, and keep each transaction to one chunk. Why: an unbounded `all()` works in tests and runs
  out of memory or holds locks for minutes on a real tenant. Test: a test with more rows than one chunk passes and
  peak memory stays below the budget. Source: reproducible with the test above; batching and keyset rules in
  `postgres-production`.
- [invariant] Application code never runs Redis `KEYS`; it uses `SCAN`, sets or tags. Why: `KEYS` is O(N) over
  the whole keyspace and blocks the server. Test: a CI grep for `->keys(` and `KEYS ` outside debugging tools is
  empty. Source: https://redis.io/docs/latest/commands/keys/, "Don't use `KEYS` in your regular application code"
  (verified 2026-11-03).
- [default] Size every measurement for 100 times the largest current tenant: seed that volume (rows, recipients,
  events per minute) and measure query count, p95 time and memory there. Trade-off: seeding and measuring take
  time on every feature. Deviate only with an ADR that names this trade-off. Proof: the report states the seeded
  volume next to each number.
- [default] Analytical queries (column stores, time series) have a bounded time window, use the partition and
  sort key, and report bytes and rows scanned from the engine's own query log. Trade-off: users cannot query open
  ranges. Deviate only with an ADR that names this trade-off. Source: the `clickhouse-best-practices` plugin for
  ClickHouse rules; reproducible: the query log row for the feature's query.

## Procedure

1. Gate: does the change read or write stored data, send messages, enqueue work or run in a worker? If not,
   report "no data or traffic impact" with the reason and stop.
2. List the surfaces the change touches: endpoints, pages, jobs, broadcasts, mails, exports, schedules.
3. Read the volumes: largest tenant today (rows, users, subscribers, events per minute) and the plan's budget.
   Multiply by 100.
4. Measure per surface: query count and time with a frozen clock at N = 1 and at the seeded volume; lazy loading
   on; memory for jobs and loops.
5. Plans: `EXPLAIN (ANALYZE, BUFFERS)` on the production engine for each new or changed query, writes inside a
   rolled-back transaction. Tie each index to its query.
6. Cache, fan-out and paid messages: write the invalidation test, the fan-out formula and the cost per action.
7. Workers: static state review and the memory loop.
8. Write findings in the fixed format, sorted by magnitude. Separate what you fixed from what needs a decision.
9. Re-run the budget tests after each fix. Hand over only with the tests green and the numbers in the report.

## Traps

- A query-count test that compares two requests without a frozen clock is green on most runs and red when a
  second boundary falls between them.
- A terminating callback that stamps a "last used" column runs once per request in production but accumulates in
  a test process that reuses one application, adding writes to later requests.
- `with()` added on suspicion fixes nothing measurable and inflates every payload. Eager-load what the response
  renders.
- A plan taken on the test database engine (often SQLite) says nothing about PostgreSQL.
- An index on `(tenant_id)` next to a new index on `(tenant_id, created_at)` is redundant.
- A cached page fragment keyed without the tenant serves one tenant's data to another.
- A broadcast that serializes a model with loaded relations sends kilobytes per subscriber per event.
- A job retried after a timeout sends its SMS again unless the send is recorded before the retry can run.
- A queue worker that runs for days holds the code and the static state from its start.

## Done when

- Each touched endpoint and page has a green query-budget test with a frozen clock, constant in N.
- Each new index names its query and has a plan at representative volume on the production engine.
- Each cache has a tenant-scoped key, TTL, tags and an invalidation test.
- Fan-out and paid-message cost are stated as formulas with the 100x volume plugged in, with retry and dedupe
  tests.
- Worker code has no request state in statics, a flat memory loop and recycle limits.
- The report lists every finding in the fixed format, fixed and open items apart.

## References

- [references/finding-format.md](references/finding-format.md): load when writing the report, or to see example
  findings for each dimension.
- [references/measurement-recipes.md](references/measurement-recipes.md): load when writing the budget test, the
  memory loop, the fan-out assertion or the plan check, with Laravel and PostgreSQL examples.

## Sources

- https://laravel.com/docs/12.x/database#listening-for-query-events: query events with SQL and time, verified
  2026-11-03.
- https://laravel.com/docs/12.x/eloquent-relationships#preventing-lazy-loading: lazy loading throws when
  prevented, verified 2026-11-03.
- https://www.postgresql.org/docs/current/using-explain.html: `ANALYZE` executes the statement, `BUFFERS`, toy
  tables do not predict large ones, verified 2026-11-03.
- https://laravel.com/docs/12.x/cache#cache-tags: drivers without tag support, verified 2026-11-03.
- https://laravel.com/docs/12.x/octane#managing-memory-leaks: static arrays leak, 500-request default recycle,
  verified 2026-11-03.
- https://laravel.com/docs/12.x/queues#running-the-queue-worker: long-lived workers keep state, `--max-jobs`,
  `--max-time`, `--memory`, verified 2026-11-03.
- https://redis.io/docs/latest/commands/keys/: `KEYS` warning, verified 2026-11-03.
