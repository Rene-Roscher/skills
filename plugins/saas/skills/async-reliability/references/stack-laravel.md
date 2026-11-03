# Laravel queues and scheduler

Load when the project uses Laravel queues, Horizon or the scheduler. Checked against the Laravel 12.x docs on
2026-11-03 (https://github.com/laravel/docs/blob/12.x/queues.md and
https://github.com/laravel/docs/blob/12.x/scheduling.md). The 13.x docs show the same features with PHP attributes
(`#[UniqueFor(3600)]`); re-read the docs at your installed version. Worker state under Octane and long-lived
workers belongs to `laravel-production-runtime`.

## Mapping

| Rule | Laravel feature | Note |
|---|---|---|
| dispatch after commit | `Job::dispatch(...)->afterCommit()`, or `after_commit => true` on the connection | the global option also defers queued listeners, mail, notifications and broadcasts |
| timeout below redelivery | `$timeout` on the job, `--timeout` on the worker, `retry_after` on the connection | docs: "The `--timeout` value should always be at least several seconds shorter than your `retry_after` configuration value"; job timeouts need PCNTL |
| network timeouts | `Http::timeout(...)->connectTimeout(...)` | docs: IO such as sockets or outgoing HTTP "may not respect your specified timeout" |
| bounded retries | `$tries`, `$maxExceptions`, `backoff()` returning an array | `backoff()` arrays have no jitter; add it in the method |
| dead letter | `failed()` on the job, `failed_jobs` table, `queue:retry` | write your own report; the table alone alerts nobody |
| unique job | `ShouldBeUnique`, `uniqueId()`, `$uniqueFor` | all dispatchers must share one cache server; `ShouldBeUniqueUntilProcessing` unlocks before the job runs |
| no overlap | job middleware `WithoutOverlapping($key)->expireAfter($seconds)` | needs a cache driver with atomic locks |
| scheduler | `->withoutOverlapping($minutes)->onOneServer()` | overlap lock default 24 hours; closures need `->name()` for one-server |
| urgency queues | `->onQueue('paging')`, one worker or Horizon supervisor per queue | a general worker may use `--queue=paging,notifications` as a fallback |

## Backoff with jitter

```php
public function backoff(): array
{
    $base = 2; $cap = 300;
    return array_map(
        fn (int $n) => random_int(0, min($cap, $base * 2 ** $n)),
        range(1, $this->tries - 1),
    );
}
```

## Config test

```php
it('keeps every job timeout below retry_after', function () {
    $retryAfter = config('queue.connections.redis.retry_after');
    foreach (jobClasses() as $class) {            // project helper listing job classes
        $timeout = (new ReflectionClass($class))->getDefaultProperties()['timeout'] ?? 60;
        expect($timeout + 10)->toBeLessThan($retryAfter, $class);
    }
});
```

## Traps

- `Queue::fake()` and the `sync` driver hide ordering, delay and redelivery. Run the double-run test by calling
  `handle()` twice, not by dispatching twice to `sync`.
- `retry_after` exists per connection; Amazon SQS has none and uses the queue's visibility timeout instead.
- A worker started without `--timeout` uses 60 seconds; a job `$timeout` overrides it for that job.
- Horizon config often lives only in local or staging; production may run plain `queue:work` processes. Check
  which one runs before trusting a supervisor setting.
- Long-running workers keep code in memory: restart them after a deploy or config change.
