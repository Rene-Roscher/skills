# Guard artifacts

Load when setting up the guard tests in a project, or checking which exist. Each one starts with a one-line
`Why:` comment and gets one recorded red run. Paths are suggestions; follow the project's layout.

| Artifact | Proves | Rule |
|---|---|---|
| `tests/bootstrap.php` runtime-minor guard reading `config.platform.php` | tests run on the production minor | PHP minor |
| `phpunit.pg.xml` (or equivalent) and a required CI job with its own database | the suite passes on PostgreSQL | engine |
| `tests/Feature/Database/PostgresDriftCanaryTest.php`, PostgreSQL only | jsonb, aborted transactions, rounding, CHECK, aliases, order | engine |
| `tests/Feature/Architecture/TestEnvironmentPinningTest.php` | every pin reaches `config()` | hermetic env |
| `Http::preventStrayRequests()` in `tests/Pest.php` | no test calls out | hermetic env |
| `tests/Feature/Architecture/OctaneFlushGuardTest.php`, both directions | flush list holds own keys only, and all of them | flush list |
| Tenant-context leak test | nothing of tenant A is bound after an unauthenticated request | tenant context |
| Two-requests regression test per stateful service used by controllers | no stale memo across requests | long-lived state |
| Two-tenants job test per tenant-binding job | no tenant state across jobs in one worker | long-lived state |
| `tests/Feature/Queue/WakeUpQueueSeparationTest.php` | wake-up jobs on their queue, one dedicated worker, backlog metric | wake-up queue |
| Guard tests under `Queue::fake()` | dedupe guards read synchronous data | async data |
| `tests/Feature/Queue/RetryAfterTest.php` | `retry_after` exceeds every job timeout | retry_after |
| Job construction tests without web-only providers | jobs run from their arguments alone | explicit parameters |
| `+01:00` input test per time-accepting endpoint | stored instant is the UTC equivalent | UTC |
| Rendered-mail test per mailable with links, mailer-pinning test | links survive the text part, right mailer | mail |
| Strict-mode test | the three `prevents*()` flags are on in tests | strict Eloquent |
| Query-budget helper in `tests/Pest.php` with `freezeTime()` built in | hot paths stay within budget | query budgets |
| Config tests: `redis.client`, queue and session connection differ from cache, debounce store | tiers and client as decided | stores |
| CI check that `tests/` imports no real broker client or production host | tests stay hermetic | hermetic env |

## Query-budget helper

```php
// tests/Pest.php
function expectQueryBudget(int $max, Closure $requests): void
{
    test()->freezeTime();
    DB::flushQueryLog();
    DB::enableQueryLog();
    $requests();
    expect(count(DB::getQueryLog()))->toBeLessThanOrEqual($max);
    DB::disableQueryLog();
}
```

Pair the absolute budget with a scaling check: the count for ten records is close to the count for one.
