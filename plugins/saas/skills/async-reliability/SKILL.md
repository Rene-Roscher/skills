---
name: async-reliability
description: "Makes background work safe under redelivery: idempotent handlers with a stable key, backoff with jitter, dead-letter with replay, unique and overlap locks, timeouts below the redelivery window, dispatch after commit, urgency-split queues, capped paid or paging sends, kill switches, lag alerts. Use when adding or reviewing a job, consumer, scheduled task or notification. Not for outgoing webhooks."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Async reliability

This skill decides how queued jobs, stream consumers, scheduled tasks and notification sends behave when a message
arrives twice, a worker dies mid-run, a provider hangs or a bulk dispatch floods a queue. It is stack-neutral; queue
and broker syntax stays with the vendor docs and the stack references below. Outgoing webhook delivery to customer
endpoints belongs to `egress-and-webhooks`, tenant context in jobs to `tenant-isolation`, Laravel worker state to
`laravel-production-runtime`. The failure this prevents: a retried job that charges, pages or deletes twice, or an
alert that waits behind a newsletter.

## Applies when / does not apply

- Applies: a new or changed job, listener, stream consumer, scheduled task, notification, mail or SMS send, retry
  policy, queue or worker definition, feature flag that gates background work, a dead-letter or replay tool, a
  question such as "why did this run twice" or "why was the alert late".
- Does not apply: outgoing webhooks to customer URLs (`egress-and-webhooks`), HTTP retries inside a request the user
  waits on, database failover and backups (`high-availability`), which tenant a job may read (`tenant-isolation`).

## Rules

Most important first. Examples use a booking app: bookings, reminders by mail and SMS, on-call alerts for staff.

- [invariant] Assume at-least-once delivery and make every handler idempotent under a stable key carried in the
  message: the key is minted at dispatch (booking ID plus transition, or a dispatch UUID serialized with the job),
  never at execution, so every redelivery and retry carries the same key. The effect is claimed with a unique
  constraint or an atomic set-if-absent on that key. Why: brokers redeliver after a crash between processing and
  acknowledgement, and retries re-run the whole handler. Test: run the handler twice with the same message; exactly
  one effect row and one provider call. Source: Kafka design, "It can read the messages, process the messages, and
  finally save its position ... This corresponds to the at-least-once semantics in the case of consumer failure"
  (https://kafka.apache.org/44/design/design/, verified 2026-11-03); Amazon SQS, "there's no absolute guarantee
  that a message won't be delivered more than once"
  (https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html,
  verified 2026-11-03).
- [invariant] Anything that wakes a person or costs money per message (SMS, voice, paid push, a charge) is claimed
  once per dispatch key immediately before the irreversible call. Release the claim only when the provider
  definitely rejected the request; on an ambiguous outcome (timeout, reset after send) keep it and record the
  attempt as unknown for reconciliation. On top: caps per recipient, per tenant and a global breaker that stops
  sending, and an auto top-up that refuses while a cap is hit. Why: a job with three tries charged SMS credits
  three times when the provider accepted the message but the response timed out; a runaway loop burns credits up
  to the reload limit. Test: a fake provider that accepts and then times out, job tries set to 3; one provider call
  and one credit booked. A loop of 1,000 sends to one recipient stops at the per-recipient cap. Source:
  reproducible with the test above; AWS Builders' Library, "APIs with side effects aren't safe to retry unless they
  provide idempotency"
  (https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter,
  verified 2026-11-03).
- [invariant] Dispatch after commit: a job or event produced inside a database transaction is enqueued only after
  the commit, or written to an outbox table in the same transaction and relayed by a separate process. Jobs carry
  IDs and explicit parameters and re-read state when they run. Why: a job enqueued before commit can run against
  rows that do not exist yet or were rolled back. Test: dispatch inside a transaction, roll it back; nothing is
  enqueued. Dispatch, commit, then run; the job sees the committed row. Source: microservices.io, transactional
  outbox, "A separate process then sends the messages to the message broker" and "a message consumer must be
  idempotent" (https://microservices.io/patterns/data/transactional-outbox.html, verified 2026-11-03).
- [invariant] A job's own timeout is shorter than the redelivery window (`retry_after`, visibility timeout, lease),
  and every network call inside the job has its own connect and read timeout shorter than the job timeout. Why:
  if the job outlives the window, the broker hands it to a second worker while the first still runs. Test: a config
  test asserts the longest per-job timeout plus a margin is below each connection's redelivery window, and an
  arch check finds no HTTP client without a timeout in job code. Source: Laravel 12.x queues, "If your `--timeout`
  option is longer than your `retry_after` configuration value, your jobs may be processed twice"
  (https://github.com/laravel/docs/blob/12.x/queues.md, verified 2026-11-03).
- [invariant] Separate queues by urgency: the queue that wakes people carries those jobs and nothing else, and the
  queue that runs failure detection carries no slow external calls. A general worker may list the paging queue
  first as a fallback. A queue whose jobs call external providers runs at least two processes, so one hung call
  does not hold every page. Why: a list-backed queue is FIFO, so a bulk dispatch ahead of a page delays the page,
  and more workers only divide that delay. In one system, detection shared a single-process queue with DNS
  lookups. Test: dispatch every wake-up job class and assert its queue name; assert the paging queue appears in
  exactly one dedicated worker definition with at least two processes. Source: reproducible with the test above.
- [invariant] Retries are bounded, back off exponentially with a cap and jitter, honour `Retry-After`, and happen
  only for errors that can succeed later. Validation errors and 4xx answers other than 408 and 429 fail at once
  unless the handler documents why it retries them.
  Non-idempotent calls are retried only with an idempotency key. Why: retries without jitter arrive in the same
  second after an outage and keep an overloaded dependency down. Test: inject the random source and clock; assert
  the delay schedule stays under the cap and differs across workers. Source: AWS Builders' Library, "When failures
  are caused by overload, retries that increase load can make matters significantly worse" and "Jitter adds some
  amount of randomness to the backoff to spread the retries around in time" (URL above, verified 2026-11-03).
- [invariant] Poison messages leave the main path: after the last attempt the message goes to a dead-letter store
  with payload, error class, attempt count and first-failure time. Replay is a command that re-enters the normal
  handler, so idempotency still applies. A report of new dead letters reaches a human, and its watermark advances
  only after the report was sent. Why: a failed wake-up call that sits in a failed-jobs table looks exactly like
  "nothing to send". Test: force a handler to throw on every attempt; the message lands in the dead-letter store,
  the next report lists it, and a replay after the fix produces one effect. Source: Amazon SQS, a dead-letter queue
  keeps failed messages "from repeatedly circulating in the main queue" (SQS URL above, verified 2026-11-03).
- [invariant] Unique and no-overlap locks live in one store shared by every dispatcher and worker, are keyed by the
  entity, and expire after a finite time longer than the job's worst-case runtime. Why: a lock in a per-process or
  per-node store lets two nodes both believe they hold it; a lock without expiry stays forever after a crash.
  Test: dispatch the same unique job from two processes against the shared store; one is enqueued. Kill a worker
  mid-job; the lock frees after its expiry. Source: Laravel 12.x queues, unique jobs need "the same central cache
  server", and `WithoutOverlapping` takes `expireAfter` for jobs that "unexpectedly fail or timeout" (Laravel URL
  above, verified 2026-11-03).
- [invariant] Each scheduled task runs on one instance per tick and never overlaps itself, with an explicit lock
  expiry. Long work is enqueued as jobs, not run inside the scheduler. Why: with several replicas every scheduler
  fires the task; Laravel's overlap lock defaults to 24 hours, so a crashed run blocks the task for a day. Test:
  run the scheduler tick in two processes; the task runs once. Source: Laravel 12.x scheduling, `onOneServer` and
  "By default, the lock will expire after 24 hours"
  (https://github.com/laravel/docs/blob/12.x/scheduling.md, verified 2026-11-03).
- [invariant] Handlers check preconditions when they run and treat "no longer applicable" as success: a reminder
  for a cancelled booking ends without sending. Why: messages are snapshots of an earlier state and can sit in a
  queue for minutes. Test: dispatch a reminder, cancel the booking, run the job; no send, job marked done. Source:
  reproducible with the test above.
- [invariant] Backlog and lag are measured per queue and per consumer group, with an alert on the oldest message
  age or lag. Every new queue or topic shows up in metrics in the same change. Why: a queue no dashboard shows can
  stall for hours unnoticed. Test: a config test lists every queue in the worker definitions and fails if one has
  no metric or alert rule. Source: Kafka monitoring, `records-lag-max` "Number of messages the consumer lags behind
  the producer by" (https://kafka.apache.org/44/operations/monitoring/, verified 2026-11-03).
- [invariant] Kill switches have their default in one accessor: a missing key means the default, only an explicit
  value changes it, and every reader (UI props, API, workers, schedulers, consumers) calls that accessor. The
  switch covers every enforcement point, works from a CLI when the web tier is down, and every toggle is audited.
  Why: a default flipped in the model but rebuilt by hand in the UI props hid a feature for six days, and an admin
  form that cast a missing key to false wrote the switch back on unrelated saves. Test: with the key absent, assert
  the value through each reader's real output, never through a copy of the expression; save the admin form for an
  unrelated field and assert the key is still absent. Source: reproducible with the test above.
- [invariant] Skipped work leaves a trace: a send skipped for a cap, a rate limit or a disabled switch records the
  reason, and a tenant whose messages were skipped is told. Why: silent skips are indistinguishable from "nothing
  happened". Test: hit the cap in a test; a skip record with the reason exists and the tenant notice is queued.
  Source: reproducible with the test above.
- [default] Backoff uses full jitter, `sleep = random(0, min(cap, base * 2^attempt))`, with a cap per job class.
  Trade-off: single retries become less predictable in exchange for spreading load after an outage. Deviate only
  with an ADR that names this trade-off. Source: AWS Architecture Blog, "Exponential Backoff And Jitter", which
  compares no jitter, full, equal and decorrelated jitter
  (https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/, verified 2026-11-03).
- [default] Within one database, after-commit dispatch plus a scheduled reconcile sweep for missed work is enough.
  Use an outbox table when the message goes to an external broker and losing it is not acceptable. Trade-off: the
  outbox adds a table, a relay process and duplicate deliveries; after-commit can lose a message if the process dies
  between commit and enqueue, which the sweep repairs later. Deviate only with an ADR that names this trade-off.
  Source: microservices.io outbox (URL above, verified 2026-11-03).
- [default] Ordering is per entity, not global: key stream messages by the entity ID so one partition holds its
  history, and let handlers drop a message whose version is older than the stored one. Trade-off: no cross-entity
  order, in exchange for parallel consumers. Deviate only with an ADR that names this trade-off. Proof: deliver
  versions 2 then 1 of the same booking; the stored state is version 2.

## Procedure

1. Gate: does the work leave the request (job, listener, consumer, schedule, notification)? If not, stop.
2. Classify the effect: reversible and free, irreversible, paid per message, or waking a person.
3. Pick the queue by urgency; paging and detection paths get nothing else.
4. Define the idempotency key at dispatch and the claim (unique row or set-if-absent) in the handler.
5. Dispatch after commit, or write to the outbox in the same transaction.
6. Set timeouts: each outbound call, then the job, then confirm both sit below the redelivery window.
7. Set retries: max attempts, backoff with cap and jitter, which errors fail at once.
8. Wire failure handling: dead-letter store, replay command, report with a send-then-advance watermark.
9. Add locks (unique, no-overlap, one-instance schedule) with a shared store and finite expiry.
10. Add caps and the kill switch for paid or paging sends; record skips with a reason.
11. Add the backlog or lag metric and alert for any new queue or consumer group.
12. Write the double-run, rollback, timeout and poison-message tests before review.

## Traps

- A guard that deduplicates by reading a log written by another queued job passes with the synchronous test queue
  and never fires in production, where the log arrives seconds later. Guard on columns written in the same request.
- A key generated inside the handler (`uuid()` at run time) is a new key on every retry and deduplicates nothing.
- Adding workers to a shared FIFO queue shortens the wait for a page but never removes it.
- The paging queue placed on the "critical" queue that fills up during a large outage, which is exactly when pages
  matter.
- A failed-jobs table nobody reads; a failure report whose watermark advances before the mail went out, so a mail
  outage swallows the failures it should report.
- A test that rebuilds the flag expression with its own default stays green while production reads the opposite.
- A unique lock in an in-memory or per-node cache works in single-node tests and does nothing across replicas.
- HTTP clients default to no timeout or a very long one; the job timeout then kills the worker mid-call.
- Single-server scheduling needs a name on scheduled closures; Laravel 12.x says closures "must be assigned a name
  if they are intended to be run on one server".

## Done when

- A double-run test proves one effect for each new handler, with the key set at dispatch.
- A rolled-back transaction enqueues nothing.
- Config tests pin timeout below the redelivery window and the paging queue to its dedicated worker.
- Paid and paging sends have a claim, caps, a kill switch with one default, and skip records.
- Poison messages land in the dead-letter store, are reported, and replay once.
- Each new queue or consumer group has a backlog or lag alert.

## References

- [references/patterns.md](references/patterns.md): load when writing the claim, outbox, dead-letter schema,
  failure report, kill-switch accessor or the backoff function.
- [references/stack-laravel.md](references/stack-laravel.md): load when the project uses Laravel queues, Horizon or
  the scheduler.
- [references/stack-kafka.md](references/stack-kafka.md): load when the project produces to or consumes from Kafka
  or a Kafka-compatible broker.

## Sources

- https://kafka.apache.org/44/design/design/: delivery semantics, at-least-once on consumer failure, verified
  2026-11-03.
- https://kafka.apache.org/44/operations/monitoring/: `records-lag-max`, verified 2026-11-03.
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html:
  at-least-once delivery, visibility timeout, dead-letter queues, verified 2026-11-03.
- https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter: retries
  under overload, idempotency before retry, jitter, verified 2026-11-03.
- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/: jitter variants compared, verified
  2026-11-03.
- https://microservices.io/patterns/data/transactional-outbox.html: outbox and idempotent consumers, verified
  2026-11-03.
- https://github.com/laravel/docs/blob/12.x/queues.md: `retry_after` versus `--timeout`, `after_commit`, unique
  jobs, `WithoutOverlapping::expireAfter`, verified 2026-11-03.
- https://github.com/laravel/docs/blob/12.x/scheduling.md: `withoutOverlapping` 24-hour default, `onOneServer`,
  verified 2026-11-03.
