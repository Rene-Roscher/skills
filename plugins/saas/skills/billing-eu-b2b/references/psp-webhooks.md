# PSP webhooks

Load when writing or reviewing a payment provider webhook handler. Provider facts carry their fetch date.
Re-read the provider docs at your SDK version before relying on them; for provider syntax use the provider's
docs or its official tooling.

## Provider facts

| Fact | Mollie | Stripe |
|---|---|---|
| Body | a single POST parameter `id`; fetch the object with the API | signed event with the full object |
| Authenticity | fetching with your API key is the check | verify the `Stripe-Signature` header; library default tolerance 5 minutes, never set it to 0 |
| Unknown IDs | return 200 | |
| Timeout and retries | 15 s timeout, 10 attempts over about 26 hours | retries for up to three days in live mode |
| Order and duplicates | | delivery order not guaranteed; duplicates happen, track event IDs |
| Idempotency keys on API calls | `Idempotency-Key` header; "Keys older than 1 hour will be removed from our cache"; same key with different parameters returns 400 | v1 keys can be pruned after at least 24 hours; a retry returns the saved response, including 500 errors; mismatched parameters error |
| Source, fetched 2026-10-31 | https://docs.mollie.com/reference/webhooks, https://docs.mollie.com/reference/api-idempotency | https://docs.stripe.com/webhooks, https://docs.stripe.com/api/idempotent_requests |

## Handler flow

1. Verify: signature where the PSP signs. For ID-only PSPs there is nothing to verify in the body; the fetch in
   step 4 is the check.
2. Store: insert the raw event into an inbox table with a unique key on the provider's event or object ID and
   `ON CONFLICT DO NOTHING`. A duplicate delivery inserts nothing and still gets a 2xx.
3. Acknowledge: return 2xx once the row is committed. If the insert fails, return non-2xx so the PSP retries.
4. Process in a job: fetch the current object from the PSP with your own credentials. Unknown or deleted IDs end
   the job without a side effect.
5. Map the fetched status to a transition (paid, failed, refunded, charged back, expired).
6. Claim the effect: insert into an effects table with a unique key (provider, external ID, transition) and
   `ON CONFLICT DO NOTHING RETURNING id`. No row returned means the effect already happened.
7. Apply the effect in the same database transaction as the claim, after comparing the settled amount and
   currency with the local record. A mismatch changes nothing and raises an alert.
8. If processing throws, the transaction rolls back the claim too, and the job retries.

## Claim in SQL

```sql
INSERT INTO payment_effects (provider, external_id, transition, created_at)
VALUES ($1, $2, $3, now())
ON CONFLICT (provider, external_id, transition) DO NOTHING
RETURNING id;
```

Name the conflict target. "ON CONFLICT DO NOTHING simply avoids inserting a row as its alternative action",
and without a target it handles conflicts with every unique constraint on the table
(https://www.postgresql.org/docs/current/sql-insert.html, verified 2026-10-31).

On PostgreSQL, a unique violation that the application catches inside a transaction leaves the transaction
aborted; every following statement fails until rollback. Insert-on-conflict avoids raising the violation.

## Framework notes

- Laravel 12 `insertOrIgnore` compiles to `on conflict do nothing` on PostgreSQL and returns the affected-row
  count, but on MySQL it compiles to `insert ignore`, which may also ignore other errors (Laravel 12 docs and
  laravel/framework v12.53.0 source, checked 2026-10-31). It sets no conflict target, so prefer the raw
  statement above when the table has other unique indexes.
- Long-lived workers (Octane, Swoole, RoadRunner, Node, Go): an SDK client held as a singleton can keep
  per-request state such as an idempotency key. Set it per call and clear it in `finally`.

## Tests

- Forged body with an unknown ID: 2xx, no state change.
- Signature with a timestamp outside the tolerance: rejected.
- Two parallel deliveries of one event: one effect (PostgreSQL).
- Paid, then refunded, then charged back on one payment ID: three effects.
- Refund delivered before paid: correct final state after both.
- PSP fetch times out: non-2xx, or the inbox row stays pending for retry.
- Settled amount one cent off: transaction stays pending, alert emitted.
