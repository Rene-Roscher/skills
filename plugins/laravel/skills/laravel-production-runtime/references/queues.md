# Queues

Load when adding a job, choosing a queue, isolating wake-up jobs, or setting `retry_after` and timeouts.
Queue syntax: https://laravel.com/docs/12.x/queues.

## Choosing a queue

- A small set of urgency tiers (for example critical, notifications, default, bulk) plus one dedicated queue
  for jobs that wake a person. The project picks the names.
- The wake-up queue carries nothing else. A Redis-backed queue is FIFO: a bulk dispatch ahead of a page delays
  the page, and more workers only share the delay.
- It has its own worker process or Horizon supervisor. A general worker may list it first
  (`--queue=wakeup,notifications`) as a fallback.
- Its backlog is a metric with an alert.

Tests: every wake-up job asserts its queue name; a config test asserts that the wake-up queue appears in
exactly one dedicated worker definition; a test asserts the backlog metric exists.

## Writing a job

- Constructor takes scalar IDs and every business parameter (tenant ID, tax rate, locale, currency). A worker
  has no tenant bound and no request.
- Load models fresh in `handle()`. Check that the record still exists and is still in the state the job
  expects.
- Dispatch from transactional code with `afterCommit()`. Leave the global `after_commit` option off unless the
  whole app is built for it.
- No dependency on providers that boot only in the web process (admin panel URL helpers, panel-specific route
  names). Build deep links from config.
- Bind tenant context inside `handle()` and forget it in `finally`.
- Make it idempotent: a unique key or a status transition guards a second run.

Test: construct and handle each job from its constructor arguments alone, with web-only providers not
registered.

## retry_after and timeouts

`retry_after` on the queue connection must exceed the longest job `$timeout` on that connection, or a slow job
is released and runs twice. A test reads `config('queue.connections.*.retry_after')` and every job's `$timeout`
and fails when the margin is gone. Background: https://laravel.com/docs/12.x/queues (job expiration and
timeouts).

## Guards and async data

A dedupe or "already done" guard reads columns written in the same request, never a table a job fills later
(an async audit log, a projection). Test such guards under `Queue::fake()`, because the sync queue writes the
async data immediately and the guard looks correct.

## Horizon or plain workers

Both satisfy these rules. Horizon needs a Redis queue connection and does not support Redis Cluster
(https://laravel.com/docs/12.x/horizon). Which one runs in production is a project choice.
