# Downgrade and metering

Load when handling downgrade, cancellation or suspension, add-on clamping, per-cycle resets or purchased packs.
The example is an invoicing app.

## Contents

- Downgrade behaviours per key
- Order of a downgrade
- Suspension versus downgrade
- Allowances, resets and packs
- What the customer sees

## Downgrade behaviours per key

| Behaviour | Keys in the example | Effect | Reversible |
|---|---|---|---|
| block new | invoices per month, API access, e-invoice formats | nothing changes; new use over the limit is refused | yes |
| pause excess | seats, customers with active recurring invoices | newest over the limit are deactivated with `reason = plan_limit` | yes, on upgrade |
| lossy | retention days, number of sending domains | data or settings are removed after a grace period | no |

Every key in the schema has exactly one of these. A key whose natural behaviour is lossy gets the most protection:
preview, notice, grace, and a floor.

Pause excess:

- Pick the newest records first, so the oldest working set survives.
- Store the reason on each record; a record the customer paused by hand keeps its own reason and is not
  reactivated by an upgrade.
- Reactivation reads `limit()`, enforcement reads the enforcement value; both use the same usage function.
- Upgrade reactivates oldest first, up to the new limit, with the same IDs.

Lossy:

- Before confirmation, show concrete numbers ("invoices older than 12 months, currently 1,240 documents, will be
  deleted on [date]").
- Start the grace period at the effective date of the downgrade, not at the click.
- Notify the owner when the downgrade takes effect and before the grace period ends.
- An upgrade during the grace period cancels the removal.

## Order of a downgrade

1. At period end, switch the subscription to the new plan (the switch is billed by `billing-eu-b2b`).
2. Clamp add-on quantities to what the new plan allows; record the reduction.
3. Invalidate cached entitlements for the tenant.
4. Run each key's downgrade behaviour using the freshly resolved values.
5. Send one summary to the owner with every key that changed and its numbers.

Cancellation to the free tier runs the same path with the free plan as target.

## Suspension versus downgrade

A suspension (unpaid, abuse hold) is temporary. It applies a restriction in the resolver and runs only reversible
behaviours: block new and pause excess. It does not clamp add-ons and does not start lossy grace periods. Lifting
the suspension removes the restriction and reactivates what it paused.

## Allowances, resets and packs

```sql
CREATE TABLE credit_balances (
    tenant_id   bigint NOT NULL,
    kind        text NOT NULL CHECK (kind IN ('included', 'pack')),
    key         text NOT NULL,                  -- e.g. reminder_sms
    balance     integer NOT NULL CHECK (balance >= 0),
    period_end  timestamptz,                    -- included only
    PRIMARY KEY (tenant_id, key, kind)
);

CREATE TABLE allowance_resets (
    tenant_id    bigint NOT NULL,
    key          text NOT NULL,
    period_start timestamptz NOT NULL,
    PRIMARY KEY (tenant_id, key, period_start)  -- a second reset for the same period inserts nothing
);
```

- Reset: in one transaction, insert into `allowance_resets` with `ON CONFLICT DO NOTHING`; only when a row was
  inserted, set the included balance to the plan's allowance. Packs are not touched.
- Debit: try the included balance with `UPDATE … SET balance = balance - n WHERE … AND balance >= n`; if no row
  changed, try the pack balance the same way; if neither, refuse before sending.
- The period follows the subscription's billing period, not the calendar month, unless an ADR says otherwise.
- Whether unused included credits carry over is a product decision; record it in the schema declaration.
- Warn at a threshold before the balance runs out, not after a send failed.

## What the customer sees

- Usage and limit per key, from the resolver, with the restriction reason when one applies.
- For soft limits: what degrades above the limit.
- For pending downgrades: what will be paused or removed and when.
- For overrides: nothing internal; the effective value is enough, and the billing view lists contract terms.
