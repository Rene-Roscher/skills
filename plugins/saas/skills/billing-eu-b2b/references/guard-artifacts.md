# Guard artifacts

Load when adding the billing guards to a repository. Each one turns a rule into a failing build. Names are
examples; use the repository's conventions.

| Guard | Rule it enforces | Fails when |
|---|---|---|
| No-float-money check (static rule or script) | integer money | Float casts, `round`, `floor`, `ceil` or `/` on amounts appear in billing code outside the allowlisted money helper |
| Money helper property test | integer money | The helper differs from an exact decimal reference for any cent value and configured rate |
| Runtime version guard in the test bootstrap | integer money | The running minor version differs from production's |
| Charge-equals-invoice test | one tax computation | The charged amount differs from the invoice's BT-112 for a mixed basket |
| Tax resolver table test with a recorded VIES fixture | explicit tax inputs, reverse-charge proof | Any row returns the wrong treatment or rate; reverse charge is granted for unavailable or mismatched IDs |
| Webhook concurrency test (PostgreSQL) | claim once | Parallel deliveries produce two effects; paid, refunded and charged back on one ID produce fewer than three |
| Forged-webhook test | verify and fetch | An unknown ID changes state or gets a non-2xx |
| Record-then-charge test | record, then charge | The PSP is called inside a transaction; a PSP exception leaves no pending row; two attempts charge twice |
| Renewal claim test | per-period claim | Two stale runs charge twice or advance the period twice |
| CHECK constraint migration plus a test | constraints | The impossible write succeeds on PostgreSQL |
| Quota concurrency test (PostgreSQL) | serialized limits | More than one of N parallel creates at limit minus one succeeds |
| E-invoice validation job | no negative prices, validation | The pinned validator reports an error, or an unlisted warning, on any golden invoice |
| Invoice line order golden test (PostgreSQL) | deterministic order | The rendered invoice differs from the golden file |
| Phantom state scan | model written states | A status case has no writer, or a KPI query returns 0 on its seeded fixture |
| Reconcile command test | record-then-charge, invoices off the payment path | A stuck pending row or a succeeded charge without an invoice goes unreported |
| Fixture provenance test | recorded fixtures | A fixture lacks its source and recording date |

## No-float-money check

Start with a text search over the billing namespace and grow it into a static-analysis rule when the project
has one:

```text
patterns: \(float\)  floatval\(  \bround\(  \bfloor\(  \bceil\(  [^/]/[^/*]  \*\s*1\.\d
scope:    the billing code directories
allow:    one file listing the money helper's path, each entry with a one-line reason
```

The division pattern produces noise; restrict it to lines that mention amount variables (`amount`, `net`,
`gross`, `price`, `tax`, `total`) or use the static-analysis rule.

## E-invoice validation job

1. Download the pinned KoSIT validator and XRechnung configuration releases, and verify their checksums.
2. Generate the golden invoices from fixtures with the application's own generator.
3. Run the validator over them and fail on errors and on warnings outside the allowlist.
4. Keep the generated XML as a build artifact for review.
