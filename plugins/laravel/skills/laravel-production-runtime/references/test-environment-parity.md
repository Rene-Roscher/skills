# Test environment parity

Load when editing the PHPUnit config, env pins, the runtime-minor guard or production boot defaults, or when CI
and local results differ.

## Contents

- Differences to name
- Runtime-minor guard
- Env pins that apply
- Hermetic defaults
- Production boot defaults

## Differences to name

Before trusting a green run, list which of these differ from production for the code you changed:

| Difference | What it hides | Check |
|---|---|---|
| SQLite instead of PostgreSQL | aborted transactions, jsonb, rounding, CHECK, order | PostgreSQL lane |
| host PHP minor instead of the production minor | numeric and library behaviour changes | runtime-minor guard, production-equal container |
| sync queue | ordering, async-written data, worker boot | `Queue::fake()` tests, job tests without web providers |
| forced env values | pins that never applied | env-pinning test |
| `Mail::fake()`, `Notification::fake()` | templates never render | rendered tests |
| same-second timestamps | ordering and once-per-second writes | `freezeTime()`, explicit order |
| schema from migration files | migrations pending in a real environment | `migrate:status` against that environment |
| one controller instance per test | stale or hidden memo state | two-requests tests |

## Runtime-minor guard

`tests/bootstrap.php`, loaded through the PHPUnit `bootstrap` attribute:

```php
<?php

declare(strict_types=1);

$composer = json_decode(file_get_contents(__DIR__.'/../composer.json'), true, flags: JSON_THROW_ON_ERROR);
$target = $composer['config']['platform']['php'] ?? null;          // for example "8.4.27"
$running = PHP_MAJOR_VERSION.'.'.PHP_MINOR_VERSION;

if ($target !== null && ! str_starts_with($target.'.', $running.'.') && getenv('ALLOW_PHP_MINOR_MISMATCH') !== '1') {
    fwrite(STDERR, "Tests need PHP {$target} (composer.json config.platform.php), this is PHP ".PHP_VERSION.".\n"
        ."Run them in the production-equal container, or set ALLOW_PHP_MINOR_MISMATCH=1 for a deliberate local run.\n");
    exit(1);
}

require __DIR__.'/../vendor/autoload.php';
```

Keep `require.php` and `config.platform.php` consistent. CI pins the image or the PHP setup step to the same
minor.

An example of minor-version drift: PHP 8.4 removed "pre-rounding" from `round()`
(https://github.com/php/php-src/blob/PHP-8.4/UPGRADING). `round(374.49999999999994)` gives 375 on PHP 8.3.10 and
374 on PHP 8.4.27 (reproduced 2026-10-31).

## Env pins that apply

As read in phpunit 12.5.8 (`src/TextUI/Configuration/PhpHandler.php`) and vlucas/phpdotenv v5.6.3:

- `<env name="X" value="v" force="true"/>` calls `putenv()` and sets `$_ENV`. Without `force`, an existing value
  wins.
- `<server name="X" value="v"/>` sets `$_SERVER` unconditionally.
- Laravel's env repository reads `$_SERVER` first, then `$_ENV`.
- In the CLI, the container's environment variables are in `$_SERVER`. So a container value beats a forced
  `<env>` pin. Pin values that must win with `<server>`.

Prove it with a test that walks the PHPUnit config and compares each pin with the resolved value:

```php
it('applies every pinned test value', function (): void {
    $xml = simplexml_load_file(base_path('phpunit.xml'));
    foreach ($xml->php->server as $pin) {
        expect(env((string) $pin['name']))->toBe((string) $pin['value']);
    }
    expect(config('database.default'))->toBe('pgsql'); // plus one assertion per config key that matters
});
```

## Hermetic defaults

- `Http::preventStrayRequests()` in `tests/Pest.php`, so a missed fake fails instead of calling out.
- Message buses and brokers are faked globally.
- Metrics and analytics stores point at an unroutable address by default. A test that deletes or purges rows
  must never reach a shared dev store, where low test IDs collide with real dev records.
- Integration tests against real infrastructure are opt-in through an env flag and use their own database.
- OAuth client IDs, mail transports and payment keys are pinned to test values. A test asserts that none of
  them equals the value in the developer's `.env`.

## Production boot defaults

Set in a service provider, each with a test that boots the app with the production environment:

- `Date::use(CarbonImmutable::class)`, so `->addDay()` on a model attribute never moves another reference to
  the same instance.
- `DB::prohibitDestructiveCommands(app()->isProduction())` (present in framework v12.53.0,
  `src/Illuminate/Support/Facades/DB.php`), so `migrate:fresh` and similar commands refuse to run.
- Password rules with `uncompromised()` outside tests.
