# Charge lifecycle

Load for subscribe, renew, retry, reconcile, dunning and suspension. The example is a project tool sold per
seat with monthly and annual plans.

## Record, then charge

1. In one database transaction: create the pending transaction with a deterministic idempotency key (for
   example `renewal:[subscription id]:[period end]` or `checkout:[order id]`), apply credits, and advance any
   state that the charge depends on. Commit.
2. Outside any transaction: call the PSP with the same key as the PSP idempotency key and in the PSP metadata.
3. Store the PSP's external ID on the pending row.
4. The webhook finds the row by external ID, or by the key from metadata when step 3 never ran.
5. A scheduled reconcile command: pending rows with an external ID are polled at the PSP; pending rows without
   one, older than an agreed number of hours, are marked failed and reported.

A test asserts that no database transaction is open when the PSP client is called. In Laravel the fake client
can record `DB::transactionLevel()` at call time and the test expects 0.

## Renewals

- One claim per period: a unique key on (subscription, period end). The renewal run that wins the claim
  creates the transaction and advances the period in the same transaction.
- The charge job has one try. A failed charge goes to dunning, not to an automatic job retry, because a retry
  after the period advanced computes a new key and charges the next period.
- Two stale runs (both loaded before either committed) produce one charge and one period advance.

## Free to paid

- Goes through the full first-charge path: a transaction for the first period's full amount and a period end.
- Never through proration. Proration against a subscription without a period end has nothing to prorate
  from, and must throw.
- A CHECK constraint keeps the impossible state out, for example
  `plan = 'free' OR status <> 'active' OR current_period_end IS NOT NULL`. Test that the bad write raises on
  PostgreSQL.

## Plan and period switches

- One pro-rata function with a documented time basis (seconds or days) and explicit rounding.
- Switching monthly to annual includes the add-ons. The unused remainder of the old period becomes a credit.
- The prorated parts never add up to more than the full price.
- Table tests: mid-period upgrade, monthly to annual with add-ons, an add-on bought on the last day, a
  downgrade credit, February in a leap year.

## Dunning

An explicit state machine, for example: `past_due` after a failed renewal, scheduled retries with a fixed
maximum, `grace` after the last retry, then `suspended`.

- Before each retry, check that the payment method is still usable. An invalid mandate or an expired card
  stops retries and asks the customer for a new method.
- Each step sends one customer notice.
- Suspension is reversible: paying restores the plan, the period and the data.
- Suspension never shortens data retention while the account can still recover. Retention jobs read the
  subscription's real state, not the plan an unpaid account would fall back to.
- The retry schedule and grace length are project choices for the profile.

## States that exist

Model only states some code writes. If there is no trial, there is no `trialing` status, no "trials ending"
tile and no trial badge. A static scan lists every status case and its writers; a case without a writer fails.
