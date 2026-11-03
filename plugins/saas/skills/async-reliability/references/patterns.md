# Async patterns

Load when writing the claim, outbox, dead-letter schema, failure report, kill-switch accessor or backoff function.
SQL is PostgreSQL; the shapes carry over to other engines with an equivalent of `ON CONFLICT`.

## Contents

- Effect claim
- Paid and paging sends
- Outbox
- Dead-letter store and replay
- Failure report
- Backoff
- Kill switch accessor
- Tests to copy

## Effect claim

```sql
CREATE TABLE job_effects (
  effect_key  text PRIMARY KEY,          -- minted at dispatch, e.g. 'booking:Xy7…:reminder:24h'
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- inside the same transaction as the effect
INSERT INTO job_effects (effect_key) VALUES ($1)
ON CONFLICT (effect_key) DO NOTHING
RETURNING effect_key;                    -- no row: the effect already happened, return success
```

- Use `ON CONFLICT DO NOTHING`, not a caught unique violation: on PostgreSQL a failed statement aborts the
  surrounding transaction.
- When the effect is a call to another system and cannot share the transaction, use the two-step claim below.

## Paid and paging sends

1. At dispatch: serialize `dispatch_key` with the job.
2. In the handler, right before the provider call: atomic set-if-absent on `send:{dispatch_key}` with a TTL longer
   than the whole retry window (Redis `SET key value NX EX ttl`, or the claim table above).
3. Claim not won: another attempt already sent or is sending; end without a call.
4. Provider call:
   - accepted: record the provider message ID; keep the claim.
   - definite rejection before acceptance (4xx with a documented "not sent" meaning): release the claim, let the
     retry run.
   - ambiguous (timeout, connection reset after the request was written): keep the claim, record `unknown`, and
     let a reconcile job ask the provider by message or idempotency key where the provider supports it.
5. Caps run before the claim: per recipient per window, per tenant per window (scaled by seat count with a hard
   ceiling), and a global breaker that stops all sends and pages a human. An auto top-up checks the breaker first.

For a pure wake-up channel where a missed page is worse than a duplicate, an ADR may choose release-and-resend on
ambiguous outcomes. Write the choice down per channel.

## Outbox

```sql
CREATE TABLE outbox (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  topic       text NOT NULL,
  msg_key     text NOT NULL,       -- partition key, e.g. booking public ID
  payload     jsonb NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  sent_at     timestamptz
);
CREATE INDEX outbox_unsent ON outbox (id) WHERE sent_at IS NULL;
```

Relay loop: select unsent rows in `id` order with `FOR UPDATE SKIP LOCKED` and a limit, publish, mark `sent_at`,
commit. The relay can publish a row twice (crash after publish, before commit), so consumers deduplicate on a
message ID in the payload. Prune sent rows on a schedule.

## Dead-letter store and replay

Columns: public ID, queue or topic, handler name, payload, error class, error message (scrubbed of secrets and
personal data), attempts, first and last failure time, replayed_at, replayed_by.

- Replay runs the normal handler with the original key; it never calls the effect directly.
- Replay by ID, by handler and by time range; dry-run prints what would replay.
- Non-retryable errors (validation, mapping) go to the dead-letter store on the first attempt.

## Failure report

```text
every 15 minutes (pick per product):
  rows = dead letters with failed_at > watermark, ordered by urgency (paging first)
  if rows: send one summary to the on-call or admin channel
  only after the send succeeded: watermark = max(failed_at of rows)
```

Keep the watermark in durable storage, not in process memory, so restarts do not resend or skip.

## Backoff

```text
delay(attempt) = random_uniform(0, min(cap, base * 2 ** attempt))
if response has Retry-After: delay = max(delay, retry_after)
```

Inject the random source and clock so a test asserts the bounds. Servers that return 429 or 503 spread their own
`Retry-After` values (a random or key-hashed offset) so clients do not return together.

## Kill switch accessor

```text
feature_enabled(tenant, "reminders"):
  value = tenant.settings.get("reminders_enabled")   # absent means default
  return DEFAULTS["reminders_enabled"] if value is absent else value
```

- One `DEFAULTS` map; every reader calls `feature_enabled`. No second `get(..., false)` anywhere.
- Backfills remove keys that equal the old default instead of writing the new default.
- Admin forms hydrate from the accessor and write the key only when the field changed.
- A global switch sits in a flag store with a short cache; choose fail-open or fail-closed per flag and write it
  next to the flag. A CLI command toggles it and writes an audit entry.
- Enforcement points to list in the change: dispatch, scheduler, workers, consumers, ingest endpoints, config
  feeds to remote workers (a sentinel config hash that never equals a real one forces them to reload).

## Tests to copy

| Test | Arrange | Assert |
|---|---|---|
| double run | same message twice | one effect row, one provider call |
| rollback | dispatch in a transaction, roll back | queue empty |
| ambiguous send | fake provider accepts then times out, 3 tries | one call, claim kept, status `unknown` |
| stale message | dispatch, change state, run | no effect, success |
| poison | handler always throws | dead-letter row, in next report, replay gives one effect |
| timeout budget | read worker and queue config | job timeout plus margin below redelivery window |
| paging queue | dispatch each wake-up job | queue name, one dedicated worker definition |
| flag default | key absent | every reader returns the default |
