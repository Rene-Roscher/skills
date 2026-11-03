# Test matrix

Load when writing the boundary tests for a key. Generate the cases from the schema so a new key without tests fails
the suite. Run the concurrency cases on PostgreSQL; an in-memory database does not show the race.

## Per count limit (hard)

| Case | Setup | Expect |
|---|---|---|
| below | usage = limit − 1 | create succeeds |
| at | usage = limit | create refused, 4xx, error names key, limit, usage |
| zero | limit = 0 | first create refused |
| unlimited | limit = unlimited, usage far above any plan value | create succeeds |
| override up | plan limit L, override L + 10, usage = L | create succeeds |
| override expired | override expired yesterday, usage = plan limit | create refused, no job run needed |
| add-on | plan limit L, add-on +2, usage = L + 1 | create succeeds |
| add-on on closed | plan limit 0, buy add-on | purchase refused |
| restricted | suspended tenant with a high override | create refused, error names the restriction |
| viewer scope | member who sees 1 of L records, usage = L | create refused |
| parallel | usage = L − 1, N concurrent creates | exactly one succeeds, others get the domain error |
| every channel | web, API, import, job, tool at limit | same refusal everywhere |

## Per soft limit

- Above the limit the action succeeds and the stated degradation happens (for example only the first N
  recipients are notified, oldest first).
- The warning appears at the configured threshold.

## Per feature and set

- Off: the gated route or tool returns the refusal; the UI hides the action.
- On through an override: allowed. Override expired: refused.
- Set: a value outside the plan's set is refused; values inside are allowed.

## Downgrade and suspension

- Pause excess: downgrade, then upgrade; every paused record returns with the same ID; records paused by hand stay
  paused.
- Lossy: during grace, data beyond the new limit still exists; an upgrade in grace cancels removal.
- Add-ons clamped on downgrade, not on suspension.
- Suspension then reinstatement restores everything it paused.

## Allowances and packs

- Reset twice for one period: one reset.
- Reset leaves pack balance unchanged.
- Included consumed before packs.
- Parallel debits never drive a balance below zero.

## Schema and architecture

- Completeness: every plan defines or inherits every key; every count key has a usage function and a matrix entry.
- Only the resolver reads plan definitions, override rows and add-on rows.
- No comparisons with plan names outside the plan catalog.
- A custom plan copied from a standard plan passes the same matrix.
