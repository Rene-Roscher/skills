# Laravel

Load in a Laravel project. Syntax lives in the Laravel docs (https://laravel.com/docs/12.x/mail and
https://pestphp.com/docs/arch-testing); this file keeps the decisions.

## Mail failover

- Configure the `failover` mailer with real transports only. `log` and `array` belong to local and test
  environments as the default mailer, never inside a production failover list.
- Queue the mail and give the job a bounded number of tries. The failed-jobs table can serve as the
  dead-letter record; add an alert on new rows for mail that matters.
- Write the test that makes every transport throw. It is the only proof that the chain fails visibly.
- Read the mechanics in the failover reference before setting `retry_after`, and check your version's
  `MailManager` for where that value is read.
- Under long-lived workers (Octane, queue workers), resolved mailers can outlive one request or job. The rules
  for request state in long-lived workers live in `laravel-production-runtime`.

## Provider resolver

- Bind each capability interface in a service provider. For per-resource providers, bind a resolver class
  that maps the stored enum value to an adapter class and throws on an unknown value.
- Keep provider credentials in `config/services.php`, read through `config()`, never through `env()` outside
  config files.
- Custom mail or notification channels go through one dispatch service. A second class that calls an
  adapter's send method directly is the two-paths trap.

## Architecture rule

```php
arch('payment SDK stays in its adapter')
    ->expect('Stripe')
    ->toOnlyBeUsedIn('App\Billing\Adapters');
```

`toOnlyBeUsedIn()` and `not->toBeUsedIn()` are Pest architecture expectations (Pest docs, Architecture
testing, verified 2026-10-31). Use one rule per vendor SDK namespace.

## Validated caching of upstream responses

`rene-roscher/conditional-cache-laravel` (MIT; PHP 8.2+, Laravel 11.24+, 12 or 13; README verified
2026-10-31) adds `rememberWhen`, `rememberForeverWhen` and `flexibleWhen`, which store a value only when a
validator accepts it. With `retryAfter` and a `default`, a rejected value leaves the default under a separate
marker key for the given seconds, and the callback does not run again inside that window; `Cache::forget()`
clears the marker. With `lock`, one process computes a missing value while the others wait; the store must
support locks. The package goes through the same admission check as any other dependency.
