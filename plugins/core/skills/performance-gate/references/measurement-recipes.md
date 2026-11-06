# Measurement recipes

Examples use Laravel with Pest and PostgreSQL. The shape carries over to other stacks: count queries per request,
freeze time, seed volume, read the plan on the production engine.

## Contents

- Query budget with a frozen clock
- Lazy loading
- Plans on the real engine
- Fan-out and paid messages
- Memory in long-lived code
- Data-heavy views: cold, warm, failing source, stampede
- Seeding 100x
- Monitoring data

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

## Data-heavy views: cold, warm, failing source, stampede

Write the widget table first: widget, source, query or call, cost cold, freshness the user needs, cache key scope
(tenant, permission scope), TTL. Then measure four things at the seeded volume.

```php
beforeEach(fn () => $this->owner = Tenant::factory()->withSeededVolume()->create()->owner);

it('loads the dashboard frame cheaply and the widgets warm from cache', function () {
    $this->freezeTime();
    $owner = $this->owner;
    [$frame] = queryBudget(fn () => $this->actingAs($owner)->get('/dashboard')->assertOk());
    expect($frame)->toBeLessThanOrEqual(4);                 // frame only, constant as widgets are added

    Cache::flush();
    [$cold, $coldMs] = queryBudget(fn () => $this->actingAs($owner)->getJson('/dashboard/widgets/revenue'));
    [$warm] = queryBudget(fn () => $this->actingAs($owner)->getJson('/dashboard/widgets/revenue'));
    expect($warm)->toBe(0);                                  // report $cold and $coldMs as the cold cost
});

it('renders the other widgets when one source fails', function () {
    $owner = $this->owner;
    $this->mock(PaymentsApi::class)->shouldReceive('totals')->andThrow(new ConnectionException('down'));
    $this->actingAs($owner)->getJson('/dashboard/widgets/payments')->assertStatus(503);
    $this->actingAs($owner)->getJson('/dashboard/widgets/revenue')->assertOk();
});
```

- The test cache store must support what production uses (tags, locks); `array` supports locks, `file` and
  `database` do not support tags.
- Stampede: in a staging run, let the widget's entry expire, then send 20 concurrent requests (`hey -n 20 -c 20`,
  `ab`, k6) and count how often the computation ran (a counter or a log line inside the closure). One run is the
  pass; 20 is the stampede.
- Cost per view: cold queries and database time times the share of cold views (1 / views per TTL window), plus
  paid calls per view. Put the number in the report and in the plan's Cost model.
- With a permission-dependent widget, read it as an admin and then as a member with a warm cache; the member must
  not get the admin's number.

## Seeding 100x

Seed with factories in chunks inside one transaction per chunk, or with `INSERT ... SELECT generate_series(...)`
for large tables. Keep the seed script in the repository so the measurement can be repeated.

## Monitoring data

If an APM or error tracker reports slow transactions or N+1 groups, take the endpoint and span from there, then
reproduce locally with the budget test before changing code.
