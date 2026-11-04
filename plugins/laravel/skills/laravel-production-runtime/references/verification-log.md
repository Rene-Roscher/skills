# Verification log

Load before relying on a version-bound fact. Each line names the file it was read in and the version. If the
target lockfile has another version, re-read that file there before stating the fact; if it moved or changed,
say so instead of repeating this log. Checked 2026-10-31.

## laravel/octane v2.17.5

- `src/ApplicationGateway.php` `terminate()`: dispatches `RequestTerminated`, then calls
  `$route->flushController()` when the route has it.
- `src/Worker.php` `handle()`: `terminate()` runs only after a response was sent without a Throwable escaping
  the gateway. On a worker error, `handleWorkerError()` runs instead, so `flushController()` is skipped for that
  request. The sandbox is flushed in `finally` either way.
- `src/Listeners/FlushTemporaryContainerInstances.php`: resets scope, forgets scoped instances, then calls
  `forgetInstance()` for each `octane.flush` key. Registered on `OperationTerminated` in the stock config.
- `src/Listeners/`: `GiveNewApplicationInstanceTo{AuthorizationGate,BroadcastManager,CacheManager,DatabaseManager,FilesystemManager,LogManager,MailManager,NotificationChannelManager,QueueManager,Router,SessionManager,ValidationFactory,ViewFactory}`
  and `Prepare{Socialite,Inertia,Livewire,Scout}ForNextOperation` exist.
- `src/Listeners/CreateConfigurationSandbox.php`: binds a clone of the configuration repository into each
  operation's sandbox, so a runtime `config()` write does not outlive the request.
- `src/Worker.php` `handle()`: each request runs on `clone $this->app`, made current by
  `src/CurrentApplication.php` `set()` (`Container::setInstance()`, facade root). `RequestTerminated` carries
  the base application as `$event->app`, so `FlushTemporaryContainerInstances` forgets `octane.flush` keys on
  the base application.
- `src/Listeners/FlushAuthenticationState.php`: forgets `auth.driver` and calls `forgetGuards()` on the
  resolved auth manager. `src/Listeners/FlushSessionState.php`: flushes and regenerates the session driver.
  `src/Listeners/GiveNewRequestInstanceToApplication.php`: binds the new request on both containers.
- `config/octane.php`: `flush` ships empty.
- `src/Commands/StartCommand.php`: `--max-requests` defaults to `config('octane.max_requests', 500)`.

## laravel/framework v12.53.0

- `src/Illuminate/Container/Attributes/Singleton.php` and `Scoped.php`: class attributes;
  `src/Illuminate/Container/Container.php` `getScopedTyped()` reads them when an unbound class is resolved.
  `CurrentUser`, `Authenticated`, `Auth` (resolves a guard), `Context` and `RouteParameter` exist in the same
  directory as parameter attributes.
- `src/Illuminate/Foundation/Configuration/ApplicationBuilder.php` `withSingletons()` and
  `src/Illuminate/Foundation/Application.php` `register()` (a provider's `$singletons` property) both call
  `singleton()`.
- `src/Illuminate/Routing/Route.php` `flushController()`: nulls the cached controller and computed middleware.
  No caller inside the framework.
- `src/Illuminate/Queue/QueueServiceProvider.php`: the worker's reset scope flushes log context, resets query
  duration handlers, forgets scoped instances and clears resolved facades. It does not touch `instance()`
  bindings, singletons or statics. `src/Illuminate/Queue/Worker.php` calls it before each job.
- `src/Illuminate/Database/Eloquent/Concerns/HasAttributes.php` `fromDateTime()` formats with
  `getDateFormat()`; `src/Illuminate/Database/Grammar.php` `getDateFormat()` returns `Y-m-d H:i:s`.
- `src/Illuminate/Database/Connectors/PostgresConnector.php` `configureTimezone()`: `set time zone` after
  connecting when the connection config has `timezone`.
- `src/Illuminate/Database/Eloquent/Builder.php`: `createOrFirst()` wraps the insert in
  `withSavepointIfNeeded()` and catches `UniqueConstraintViolationException`; `firstOrCreate()` falls back to it.
- `src/Illuminate/Mail/Mailer.php` `sendMailable()`: `$mailable->mailer($this->name)`.
  `src/Illuminate/Mail/Mailable.php` `send()`: uses the mailable's own mailer only for a mail factory.
- `src/Illuminate/Database/Eloquent/Model.php`: `shouldBeStrict()` calls `preventLazyLoading()`,
  `preventSilentlyDiscardingAttributes()` and `preventAccessingMissingAttributes()`; the matching `prevents*()`
  accessors and `handleLazyLoadingViolationUsing()` exist.
- `src/Illuminate/Support/Facades/DB.php`: `prohibitDestructiveCommands()` exists.
- `src/Illuminate/Foundation/Testing/Concerns/InteractsWithTime.php`: `freezeTime()` exists.
- `src/Illuminate/Http/Client/Factory.php`: `preventStrayRequests()` exists.
- `src/Illuminate/Bus/Queueable.php` and `src/Illuminate/Foundation/Bus/PendingDispatch.php`: `afterCommit()`
  exists.

## phpunit/phpunit 12.5.8 and vlucas/phpdotenv v5.6.3

- `src/TextUI/Configuration/PhpHandler.php`: `<env>` calls `putenv()` and sets `$_ENV` (existing values win
  unless `force`); `<server>` sets `$_SERVER` unconditionally.
- phpdotenv `src/Repository/RepositoryBuilder.php`: default adapters are `ServerConstAdapter`, then
  `EnvConstAdapter`. Laravel's `Env::getRepository()` builds on these defaults.

## Reproduced

- PostgreSQL 16.11: `'2024-01-01 00:00:00.6+00'::timestamptz(0)` gives `00:00:01`, `.4` gives `00:00:00`,
  `'... 00:00:00.5'::timestamp(0)` gives `00:00:01`; `'{"b":1,"a":2,"b":3}'::jsonb` gives `{"a": 2, "b": 3}`;
  `SELECT count(*)` names its column `count`.
- SQLite 3.45.1: `SELECT count(*)` names its column `count(*)`.
- PHP 8.3.10: `round(374.49999999999994)` is `375.0`. PHP 8.4.27: `374.0`.
- laravel/framework v12.53.0 container on PHP 8.3.10: on a clone of a container, `instance()` through
  `Container::getInstance()` is gone in the next clone; `instance()` through a reference to the original
  container, held by a singleton resolved before cloning, is still bound in the next clone. Checked 2026-11-04.
