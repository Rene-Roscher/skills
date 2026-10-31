# Plan limits and quotas

Load when adding a limit, enforcing a quota or changing downgrade behaviour. The example is a project tool whose
plans limit projects and seats.

## One owner for limit semantics

- A plan resolver answers which plan a tenant is on, including complimentary periods and price locks.
- A limit service answers `can(tenant, limit)`, `limit(tenant, limit)`, `usage(tenant, limit)` and
  `remaining(tenant, limit)`. Controllers, jobs and the UI ask it; nothing else reads limit config.
- Sold limits (what the plan includes) are separate from abuse caps and creation-rate budgets (what protects
  the platform). A paying customer never hits an abuse cap that the plan page doesn't mention without a clear
  error.

## Serialize the check with the insert

A count followed by an insert lets two concurrent requests both see "one left". Pick one of these:

```sql
-- 1. Lock the tenant row for the length of the transaction
SELECT id FROM tenants WHERE id = $1 FOR UPDATE;
SELECT count(*) FROM projects WHERE tenant_id = $1;
INSERT INTO projects (...) VALUES (...);

-- 2. Transaction-level advisory lock keyed by tenant and limit
--    ($1 is a bigint key the application derives from tenant and limit)
SELECT pg_advisory_xact_lock($1);

-- 3. Counters and credit balances: atomic conditional update
UPDATE credit_balances SET balance = balance - $2
WHERE tenant_id = $1 AND balance >= $2;
-- one affected row means success; zero means not enough credit
```

`pg_advisory_xact_lock(key bigint)` "obtains an exclusive transaction-level advisory lock, waiting if
necessary" and releases it at the end of the transaction
(https://www.postgresql.org/docs/current/functions-admin.html, verified 2026-10-31). Derive the key the same
way everywhere, so every code path that creates a project takes the same lock.

The losing requests get a domain error ("project limit reached"), mapped to a clean client error, never a 500.

## Downgrades and upgrades

- A downgrade never deletes. It pauses or deactivates the newest records above the new limit and stores a
  reason on each.
- An upgrade reactivates them, with the same IDs and data.
- The customer sees before confirming what the downgrade will pause.
- Test: downgrade, then upgrade, and assert every record is back with the same ID.

## Usage credits

- Debit with the atomic conditional update above. The balance never goes negative under concurrency.
- Keep included credits (reset per cycle or not, a project choice) apart from purchased packs in the data
  model, so a reset never touches what the customer paid for.
- Warn before credits run out, not after a message failed for lack of them.
- Velocity caps and the global breaker for paid channels belong to `build-vs-buy`.
