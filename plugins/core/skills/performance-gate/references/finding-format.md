# Finding format

One block per finding, sorted by magnitude, largest first. Fixed and open findings go in separate sections.

```text
[P1] N+1 on the invoice list
Location:  app/Http/Resources/InvoiceResource.php:31
Trigger:   GET /invoices for a tenant with N invoices; the resource reads $invoice->customer->name
Magnitude: 1 + N queries; measured 52 queries at N = 50, 5,002 projected at 100x the largest tenant (N = 5,000)
Fix:       eager-load customer:id,name in the controller query; budget test asserts 4 queries at N = 1 and N = 50
Status:    fixed, budget test green
```

Fields:
- Priority: P1 grows with tenant size or costs money per action; P2 constant but above budget; P3 hygiene.
- Location: `path:line` of the line that causes the cost, not of the controller that calls it.
- Trigger: the request, action or schedule, with the input that matters.
- Magnitude: the measured number with the volume it was measured at, plus the projection at 100x with the formula.
  "Not measured" with the command that would measure it is allowed; a guess is not.
- Fix: the change, and the test that keeps it fixed.
- Status: fixed (with the test), open (needs a decision, with the options), or accepted (with the ADR).

## Examples per dimension

```text
[P1] Fan-out sends the whole subscriber list in one job
Location:  app/Jobs/NotifySubscribers.php:22
Trigger:   publishing an announcement; Subscriber::where(tenant)->get() then one notification per row
Magnitude: one job holds S models; at S = 50,000 (100x) peak memory exceeds the worker limit; S notifications
Fix:       chunk by id (500), one job per chunk carrying ids; fake-queue test asserts ceil(S / 500) jobs

[P1] SMS repeated on retry
Location:  app/Jobs/SendOutageSms.php:40
Trigger:   provider timeout after the send succeeded; the job retries
Magnitude: one extra SMS per recipient per retry; 3 tries x 25 recipients = up to 75 messages for one event
Fix:       record (event, recipient) before sending, skip when present; retry test asserts one send per recipient

[P2] Index without a query
Location:  database/migrations/2026_10_01_000000_add_status_index.php:14
Trigger:   every insert and status update on orders
Magnitude: no query filters on status alone (grep and query log); (tenant_id, status) already exists
Fix:       drop the migration; name the query if one is planned

[P2] Cache without invalidation
Location:  app/Services/DashboardStats.php:18
Trigger:   Cache::remember("stats", 3600, ...) without tenant in the key or tags
Magnitude: every tenant sees the first tenant's numbers for up to one hour
Fix:       key and tag by tenant, flush the tag on the writes listed; write-then-read test

[P1] Static array in a long-lived worker
Location:  app/Support/RateCache.php:9
Trigger:   each request appends to self::$seen
Magnitude: about 2 KB per request; 500 requests until recycle = about 1 MB per worker, unbounded without recycle
Fix:       scope the memo to the request; memory loop test stays flat
```

The numbers in the examples are illustrations of the format, not benchmarks.

## Report skeleton

```text
Performance gate: [feature]
Volumes: largest tenant today [rows/recipients/events], gate volume 100x = [...]
Surfaces: [endpoints, jobs, broadcasts, mails, exports]

Fixed
  [findings]

Open (needs a decision)
  [findings with options]

Not measured
  [item, reason, command that would measure it]

Budget tests: [list with file paths], all green
```
