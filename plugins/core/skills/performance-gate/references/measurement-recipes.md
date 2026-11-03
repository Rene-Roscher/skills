# Measurement recipes

Examples use Laravel with Pest and PostgreSQL. The shape carries over to other stacks: count queries per request,
freeze time, seed volume, read the plan on the production engine.

## Query budget with a frozen clock

Put the helper in the shared test setup file so every test uses the same counter.

```php
function queryBudget(callable $request): array
{
    $count = 0; $ms = 0.0;
    DB::listen(function ($q) use (&$count, &$ms) { $count++; $ms += $q->time; });
    $request();
    return [$count, $ms];
}

it('lists invoices with a constant query count', function () {
    $this->freezeTime();
    $tenant = Tenant::factory()->create();
    Invoice::factory()->for($tenant)->create();
    [$one] = queryBudget(fn () => $this->actingAs($tenant->owner)->getJson('/api/invoices')->assertOk());

    Invoice::factory()->for($tenant)->count(49)->create();
    [$fifty, $ms] = queryBudget(fn () => $this->actingAs($tenant->owner)->getJson('/api/invoices')->assertOk());

    expect($fifty)->toBe($one)->toBeLessThanOrEqual(6);
    expect($ms)->toBeLessThan(150);
});
```

Prove the freeze matters: put `sleep(1)` between the two measurements and remove `freezeTime()`; a timestamp write
or cache expiry changes the count. Restore both.

Time budgets in tests are loose guards against order-of-magnitude regressions, not latency targets. Latency is
measured at seeded volume against the production engine.

## Lazy loading

```php
// in a service provider, outside production
Model::preventLazyLoading(! app()->isProduction());
```

A lazy access in a resource, mail or job then throws in tests.

## Plans on the real engine

Run the feature's query against PostgreSQL with seeded volume, not against the test engine.

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ... ;          -- reads
BEGIN; EXPLAIN (ANALYZE, BUFFERS) UPDATE ... ; ROLLBACK;   -- writes
```

Read: the node that uses (or misses) the index, actual rows versus estimated rows, and buffers read. Record the
query, the plan excerpt and the seeded row count in the report. Redundancy check: list the table's indexes
(`\d table`) and look for a new index whose columns are a left prefix of an existing one, or the other way round.

## Fan-out and paid messages

```php
Queue::fake(); Notification::fake();
$tenant = Tenant::factory()->hasSubscribers(1000)->create();
$this->actingAs($tenant->owner)->post("/announcements/{$a->public_id}/publish")->assertOk();
Queue::assertCount(intdiv(1000 + 499, 500));      // one job per chunk of 500
```

For paid channels, run the action twice, fail one job after the send, retry it, and assert one send per recipient
on the fake sender. State the cost line in the report: recipients x messages per recipient x unit price.

## Memory in long-lived code

```php
$handler = app(ImportRowHandler::class);
for ($i = 0; $i < 100; $i++) { $handler->handle($row); }      // warm-up
$before = memory_get_usage();
for ($i = 0; $i < 1000; $i++) { $handler->handle($row); }
expect(memory_get_usage() - $before)->toBeLessThan(256 * 1024);
```

Also read the class for `static` properties and singletons that hold request, user or tenant values.

## Seeding 100x

Seed with factories in chunks inside one transaction per chunk, or with `INSERT ... SELECT generate_series(...)`
for large tables. Keep the seed script in the repository so the measurement can be repeated.

## Monitoring data

If an APM or error tracker reports slow transactions or N+1 groups, take the endpoint and span from there, then
reproduce locally with the budget test before changing code.
