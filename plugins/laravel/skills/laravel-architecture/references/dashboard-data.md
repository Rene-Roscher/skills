# Dashboard data

## Contents

- Controller: map widgets to load modes, compute nothing
- Widget cache
- Rollups for heavy KPIs
- Measure cold and warm

The server side of a page with several widgets: one query class per widget, a tenant-scoped cache with a TTL per
widget, stale-while-revalidate with a lock on the cold path, rollups for heavy KPIs, and cost measured cold and
warm. The Vue side (deferred groups, `WhenVisible`, skeletons, polling) is in `vue-inertia-frontend`,
references/dashboard-loading.md. Example: a project dashboard with open tasks, overdue tasks per member, a
throughput chart and an activity feed. Checked against Laravel 13.40.0 and inertia-laravel 3.x on 2026-11-06.

## Controller: map widgets to load modes, compute nothing

```php
final class DashboardController
{
    public function __invoke(Request $request, OpenTasks $open, OverdueByMember $overdue,
                             Throughput $throughput, RecentActivity $activity): Response
    {
        $scope = DashboardScope::for($request->user());   // tenant and what this viewer may see

        return Inertia::render('Dashboard', [
            'openTasks'       => $open->for($scope),                                   // cheap, first response
            'overdueByMember' => Inertia::defer(fn () => $overdue->for($scope), 'team', rescue: true),
            'throughput'      => Inertia::defer(fn () => $throughput->for($scope), 'charts', rescue: true),
            'activity'        => Inertia::optional(fn () => $activity->for($scope)),   // WhenVisible
        ]);
    }
}
```

- `Inertia::defer(callable, string $group = 'default', bool $rescue = false)`; separate groups load in parallel;
  `rescue: true` drops a failing prop from the response and reports the exception, so one broken source does not
  fail its group. `Inertia::optional` is computed only when the client asks for it with `only`.
  (https://inertiajs.com/docs/v3/data-props/deferred-props, `partial-reloads`; signature from
  `inertiajs/inertia-laravel` 3.x `src/ResponseFactory.php`, verified 2026-11-06.)
- Each widget class is one use case with one public method (`laravel-architecture`, service rule) and returns a
  readonly DTO, so the Inertia prop, an API endpoint and an export share it.

## Widget cache

```php
final class WidgetCache
{
    /** @param array{0:int,1:int} $ttl fresh and stale seconds, from the widget plan */
    public function remember(DashboardScope $scope, string $widget, array $ttl, Closure $compute): mixed
    {
        $key = "tenant:{$scope->tenantId}:widget:{$widget}:{$scope->visibilityKey}";
        $cache = Cache::tags(["tenant:{$scope->tenantId}", "tenant:{$scope->tenantId}:widgets"]);

        if (! $cache->has($key)) {
            Cache::lock("widget-lock:{$key}", 30)->block(10, function () use ($cache, $key, $ttl, $compute) {
                if (! $cache->has($key)) {
                    $cache->flexible($key, $ttl, $compute);
                }
            });
        }

        return $cache->flexible($key, $ttl, $compute);
    }
}
```

- The key holds the tenant, the widget and the viewer's visibility (role or the set of projects the viewer may
  see), never the user's display data. Two viewers with different rights never share an entry
  (`tenant-isolation`, `laravel-production-runtime` cache rule).
- TTL per widget from the plan's "fresh within" column: `[fresh, stale]` seconds for `Cache::flexible`. Inside the
  fresh window the value returns without work; inside the stale window the old value returns and a deferred
  function recomputes after the response; after it, the request computes inline
  (https://laravel.com/docs/13.x/cache, "Stale While Revalidate", verified 2026-11-06).
- `flexible` locks only the background refresh (`illuminate:cache:flexible:lock:{key}` in
  `Illuminate\Cache\Repository::flexible`, 13.x). A missing value runs the callback in every concurrent request,
  so the cold path above takes its own lock and checks again inside it. The waiting request times out with
  `LockTimeoutException`; with `rescue: true` the widget shows its error and retry.
- Locks need a store that implements them (`memcached`, `redis`, `dynamodb`, `database`, `file`, `array`) and
  one central cache server; tags need `redis`, `memcached` or `array` (Laravel 13 cache docs, "Atomic Locks",
  "Cache Tags").
- Writes that change a widget's numbers flush `tenant:{id}:widgets` (or a narrower tag) in the write path, with
  the invalidation test from `performance-gate`.

Seen on Laravel 13.40.0 with the `array` store, tagged cache and a frozen clock: cold call computes once, warm call
computes nothing, a call in the stale window returns the old value and the deferred refresh computes once, a tag
flush forces one recompute, and a held cold-path lock makes the second caller wait and then throw.

## Rollups for heavy KPIs

- A KPI that aggregates more rows than a request may read in its budget (throughput over 90 days, usage per
  member) reads from a rollup table: one row per tenant, period and dimension, written by a scheduled job.
- The job is incremental (only periods since its last watermark, plus the open period), per tenant, idempotent
  (upsert on the natural key), `withoutOverlapping()` and `onOneServer()` (`laravel-production-runtime`,
  scheduler rule), and records its last run for a staleness check.
- The widget reads the rollup through the widget cache; the request never scans raw events. The widget shows the
  rollup's "as of" time when it can be older than a few minutes.

## Measure cold and warm

Per widget, in a test with a frozen clock and realistic volume (the 100x tenant from `performance-gate`):

```php
it('computes overdue-by-member once and serves it warm without queries', function () {
    $this->freezeTime();
    [$tenant, $viewer] = bigTenantFixture();
    $widget = app(OverdueByMember::class);
    $scope = DashboardScope::for($viewer);

    DB::enableQueryLog();
    $widget->for($scope);                          // cold
    $cold = count(DB::getQueryLog());
    DB::flushQueryLog();
    $widget->for($scope);                          // warm

    expect($cold)->toBeLessThanOrEqual(3)
        ->and(DB::getQueryLog())->toHaveCount(0);
});

it('loads each dashboard group on its own', function () {
    $this->actingAs(memberUser())->get(route('dashboard'))
        ->assertInertia(fn (Assert $page) => $page
            ->has('openTasks')
            ->missing('overdueByMember')->missing('throughput')->missing('activity')
            ->loadDeferredProps('team', fn (Assert $reload) => $reload
                ->has('overdueByMember')->missing('throughput')));
});
```

- Record cold and warm query counts and wall time per widget in the plan's cost table; the warm path does no
  query, the cold path stays within the budget at 100x volume.
- `Cache::lock()->block()` measures its wait with `Carbon::now()`, so under `freezeTime()` a held lock never
  times out and the test hangs. Test the lock path with the real clock or a short-lived lock owned by the test.
  (Seen with Laravel 13.40.0, `Illuminate\Cache\Lock::block`.)
- `loadDeferredProps` and `missing` come from Inertia's Laravel testing helpers
  (https://inertiajs.com/docs/v3/advanced/testing, verified 2026-11-06). `loadDeferredProps` expects every prop of
  the group in the reload, so a rescued failure makes it fail with "Property [...] does not exist". Test the
  failure path with a raw partial request (`X-Inertia`, `X-Inertia-Partial-Component`, `X-Inertia-Partial-Data`):
  the failed prop is absent from `props` and listed in `rescuedProps`, the others are present.
- Seen with inertia-laravel 3.7.0 on Laravel 13.40.0: the group test above passes, and fails when two widgets
  share a group or when the optional prop is made eager.
