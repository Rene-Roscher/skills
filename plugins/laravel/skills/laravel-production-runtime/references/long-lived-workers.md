# Long-lived workers

Load when touching Octane, FrankenPHP worker mode, queue workers, singletons, scoped bindings, the flush list or
memo services, or when auditing an area for long-lived worker safety. Facts were read in laravel/octane v2.17.5
and laravel/framework v12.53.0 on 2026-10-31.

## Contents

- What changes under a long-lived worker
- What Octane resets for you
- State that bleeds
- Memory growth
- Configuration, connections, globals
- Request-stamped memos
- Flush guard test
- Two-requests regression test
- Audit report format

## What changes under a long-lived worker

The application boots once and one PHP process serves many requests or jobs. Anything that survives a request
(statics, singletons, container instances, registered listeners, open connections) is visible to the next one.
In a multi-tenant app that is a data-leak and authorization class, not a performance detail.

A singleton that captures the current tenant is dangerous when some request path reads it without running the
middleware that sets it: public routes, webhooks, health checks, queued jobs, another middleware group. Name
those paths in every finding.

## What Octane resets for you

On each operation Octane gives managers a fresh application instance (`GiveNewApplicationInstanceTo*`
listeners for the auth gate, broadcast, cache, database, filesystem, log, mail, notification, queue, router,
session, validation and view), rebinds the request, flushes authentication, session, queued cookies, locale,
`once()` memoization and scoped instances, and prepares Socialite, Inertia, Livewire and Scout when installed
(`src/Listeners/`). It does not know about your own `app()->instance()` bindings, the internal state of your
singletons, static properties, listeners you register at runtime, or connections you open yourself.

`config('octane.flush')` is passed to `forgetInstance()` after each operation
(`FlushTemporaryContainerInstances`). The stock config ships it empty. Put only your own instance keys there.

## State that bleeds

| Pattern | Why it leaks | Fix |
|---|---|---|
| `app()->instance('current_tenant', $t)` | the binding survives into the next request | forget it at the start of the binding middleware, list the key in `octane.flush` |
| singleton holding user, tenant, locale or request | built once per worker | `scoped()` binding, or a stateless singleton |
| `auth()->user()` stored in a constructor or property | user A stays for later requests | resolve inside the method, per call |
| `Request` injected into a singleton constructor | keeps request one forever | method injection or `request()` inside the method |
| static arrays or `static $x` memo | survive and grow | instance state on a scoped binding |
| SDK client built with one tenant's credentials | reused for the next tenant | build per request, or pass credentials per call |
| container injected into a singleton | boot-time container, misses later bindings | resolve lazily inside methods |
| service injected into a controller constructor | lives as long as the route's controller instance | method injection or call-time resolution |

## Memory growth

- Arrays on singletons that collect logs, events or results.
- Listeners or macros registered inside a request handler. The dispatcher keeps each one, and they fire more
  often with every request. Register them once in a service provider's `boot()`.
- Large models or collections held by a singleton or a static closure.
- No recycle limit. Octane's start command defaults `--max-requests` to `config('octane.max_requests', 500)`
  (`src/Commands/StartCommand.php`). Keep a limit as the safety net for slow leaks.

## Configuration, connections, globals

- Under Octane, `config([...])` inside a request changes only that request's copy: the
  `CreateConfigurationSandbox` listener clones the configuration repository for each operation. Code that
  caches a config value in a static or singleton still keeps the old one. A queue worker has no such sandbox,
  so a `config()` write in one job is visible to every later job on that worker.
- `env()` outside `config/` returns null for `.env` values once configuration is cached. Read config instead.
- Driver managers (social login, filesystem, cache, mail, notification, broadcast) are never flushed. Packages
  extend them once at boot. `forgetInstance()` rebuilds the manager from its binding, the extension is gone, and
  the driver fails from the second request on. Octane already resets these managers.
- Connections opened outside the framework (a raw Redis client, a message broker producer, an IMAP session)
  are not closed between requests. Use a managed pool, close them on `RequestTerminated`, or keep one
  stateless long-lived client that carries no tenant state.
- Dynamic `->connection()` switching per tenant leaks the previous tenant's connection unless it is reset.
- `$_GET`, `$_POST` and `$_SERVER` read directly are unreliable in worker mode. Use the `Request`.
- `Octane::concurrently()`, `Octane::table()`, the `octane` cache store, ticks and intervals are Swoole-only.
  Closures passed to them are serialized: pass scalar IDs and fetch inside.

## Request-stamped memos

A per-request memo on a long-lived service is safe when it checks a token stamped on the current request:

```php
final class VisibleProjects
{
    private ?string $stamp = null;
    private array $ids = [];

    public function forCurrentUser(Request $request): array
    {
        $stamp = $request->attributes->get('visible_projects_stamp')
            ?? tap(bin2hex(random_bytes(8)), fn ($s) => $request->attributes->set('visible_projects_stamp', $s));

        if ($stamp !== $this->stamp) {
            $this->stamp = $stamp;
            $this->ids = $this->load($request->user());
        }

        return $this->ids;
    }
}
```

`spl_object_id($request)` is not a safe stamp: PHP reuses the handle of a freed object, so a new request can
carry the old ID.

## Flush guard test

Two directions, one test file:

1. Scan `app/` for `->instance('` and `app()->instance(` calls with a string key. Every key must be in
   `config('octane.flush')`.
2. Every `octane.flush` entry must be one of those keys. Add explicit `not->toContain()` checks for the manager
   contracts you never want there (social login factory, filesystem, cache, mail, notification, broadcast).

Plus a tenant-leak test: request as tenant A, then an unauthenticated request, then assert that nothing of A is
bound in the container.

## Two-requests regression test

```php
it('reflects data created between two requests', function (): void {
    $user = User::factory()->create();
    $this->actingAs($user)->get('/projects')->assertOk();

    Project::factory()->for($user->currentTenant)->create(['name' => 'Second']);

    $this->actingAs($user)->get('/projects')->assertSee('Second');
});
```

The HTTP test client reuses the route's controller instance within a test, so this catches a stateful service
injected into the controller constructor.

## Audit report format

```text
severity    : critical | high | medium | low
file        : path:line
pattern     : row from the tables above
why         : how it bleeds or grows under a long-lived worker
reachable   : request paths that read it without the setter running
fix         : the concrete change
```

Critical: another tenant's or user's data, or an authorization bypass. High: unbounded growth or stale
connections. Medium: stale but not secret state. Low: fragile but correct today.
