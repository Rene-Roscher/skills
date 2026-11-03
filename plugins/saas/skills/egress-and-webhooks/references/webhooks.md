# Webhooks

Load when implementing signing, rotation, the retry and disable policy, the delivery log, or an inbound webhook
handler. Spec facts come from
https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md, read 2026-11-03. Payment
provider specifics and effect claims are in `billing-eu-b2b`.

## Contents

- Outgoing: message
- Outgoing: delivery and retries
- Outgoing: endpoint lifecycle
- Delivery log
- Incoming: handler flow
- Tests

## Outgoing: message

```text
webhook-id:        msg_[public ID of the delivery record]       # same on every retry
webhook-timestamp: [unix seconds of this attempt]
webhook-signature: v1,[base64 HMAC-SHA256(secret, id + "." + timestamp + "." + body)] [v1,... for each active secret]
content-type:      application/json
```

- The secret is `whsec_` plus base64 of the key bytes; HMAC uses the decoded bytes.
- Serialize the body once at event time, store it, and send those bytes on every attempt.
- The payload carries public IDs only (`dual-key-identifiers`) and the tenant's data only (`tenant-isolation`).
- Customer-defined extra headers are merged first; the three signature headers are set last and cannot be
  overridden.

## Outgoing: delivery and retries

- Send from a queue on its own worker pool, through the egress client, redirects off, short timeout.
- Delivered means a 2xx status. Everything else, including 3xx, is a failed attempt.
- Retry with exponential backoff and jitter over hours to days. The spec shows an example schedule up to about 75
  hours and calls it an example; choose and publish your own.
- Respect `Retry-After` on 429 and 503 within the overall schedule.
- Per-endpoint concurrency limit, so one slow receiver does not occupy the whole pool.

## Outgoing: endpoint lifecycle

- `410 Gone`: disable at once.
- Persistent failure (for example every attempt failing for several days, set per product): disable, keep the
  undelivered events for the retention period, notify the endpoint owner with a link to the log.
- Re-enable from the UI; offer "resend failed since" for the gap.
- Rotation: create the new secret, sign with old and new for a window the tenant chooses, then expire the old one.
  Show a secret in full only once.

## Delivery log

Per attempt: endpoint, event type, webhook ID, attempt number, started at, duration, status code or error reason,
response headers subset and the first few KB of the body (scrubbed), next retry time. Retention follows the data
retention policy. The tenant can filter by status and resend one delivery (same webhook ID, new timestamp and
signature).

## Incoming: handler flow

1. Read the raw body bytes before any framework parsing.
2. Verify: compute the expected signature, compare in constant time with each provided signature, check the
   timestamp tolerance. Providers that send only IDs have nothing to verify; the API fetch in step 5 is the check.
3. Store: insert into an inbox table keyed by provider and event ID (or provider, object ID and transition) with
   insert-on-conflict-do-nothing.
4. Answer 2xx once the row is committed; non-2xx if the insert failed so the provider retries.
5. Process in a job: fetch the object from the provider with your credentials, apply the effect idempotently
   (`async-reliability`).
6. Unknown IDs: success response, no effect, log at info level.

## Tests

- Outgoing message verifies with an official Standard Webhooks library; a flipped body byte fails.
- Two active secrets: a receiver with either verifies.
- Retry keeps `webhook-id`; `410` disables; N failures disable and notify.
- Incoming: re-encoded JSON fails verification; old timestamp fails; duplicate event gives one effect; made-up ID
  gives 200 and no effect.
