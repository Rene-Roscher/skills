---
name: laravel-production-runtime
description: "Keeps Laravel correct under production conditions tests hide: Octane and queue worker state, SQLite-green but PostgreSQL-red suites, PHP minor drift, env pins that never apply, datetime offsets, tagged caches. Use when editing Octane, queue, cache, database or mail config or phpunit*.xml, adding singletons or jobs, or when tests pass locally but fail in CI. Not for layering (laravel-architecture)."
license: Apache-2.0
compatibility: "Laravel 11 or later, PHP 8.2 or later, PostgreSQL, Valkey or Redis through PhpRedis. Octane is optional; queues may run on Horizon or plain queue:work. Vendor facts were checked against Laravel 12.53.0 and Octane 2.17.5."
metadata:
  author: "Rene Roscher"
paths:
  - "**/config/octane.php"
  - "**/config/queue.php"
  - "**/config/cache.php"
  - "**/config/database.php"
  - "**/config/session.php"
  - "**/config/horizon.php"
  - "**/config/mail.php"
  - "**/phpunit*.xml"
  - "**/tests/bootstrap.php"
  - "**/tests/Pest.php"
  - "**/tests/TestCase.php"
  - "**/app/Providers/**"
  - "**/app/**/Jobs/**"
  - "**/app/**/Mail/**"
  - "**/Dockerfile*"
---

# Laravel production runtime

This skill covers Laravel defects where the test environment looks fine and production behaves differently:
long-lived workers, the database engine, the PHP minor version, asynchronous queues, cache and session stores,
mail transport and time zones. Each rule carries a guard test. Syntax for Octane, Horizon, queues and cache
comes from the Laravel docs or the Laravel Boost MCP server's documentation search.

The meta-rule: a green signal from an environment that differs from production is not evidence. Name the
differences that apply (database engine, PHP minor, sync versus async queue, forced env values, fakes that never
render, same-second timestamps, applied versus pending migrations, one controller instance per test) and verify
each path on its own.

Vendor facts below were read on 2026-10-31 in laravel/framework v12.53.0, laravel/octane v2.17.5, phpunit
12.5.8 and vlucas/phpdotenv v5.6.3, and reproduced on PostgreSQL 16.11, SQLite 3.45.1, PHP 8.3.10 and PHP
8.4.27. Re-check each one against the target lockfile before relying on it
([references/verification-log.md](references/verification-log.md)).

This skill edits configuration and tests. It never runs commands against production databases, caches or
queues (`safe-actions`).

## Applies when / does not apply

- Applies: Octane, queue, cache, database, session, mail and test configuration; singletons, scoped bindings,
  `app()->instance()` calls; jobs, mailables and notifications; time-accepting endpoints; tests that pass locally
  and fail in CI or production.
- Does not apply: where code belongs (`laravel-architecture`), installing Octane or Horizon (vendor docs), who
  may see which tenant's data (`tenant-isolation`), Inertia SSR settings (`web-architecture`), pooler and
  zero-downtime DDL work, Kubernetes manifests.

## Rules

### Long-lived workers

- [invariant] Long-lived processes hold no request, user or tenant state. Never keep request-derived state in
  statics, singletons or services injected into a controller constructor. Resolve per-request memo services at
  call time (method injection, or `app()` inside the method), or stamp a token on the current request
  (`$request->attributes`) and compare that. Never compare `spl_object_id()`, because PHP reuses object handles.
  Why: a page served one visitor a structure memoized from another visitor's request. Test:
  `scripts/octane_scan.py` reports no blocker or high finding; one test makes two requests, changes data between
  them, and asserts that the second response shows the change; for jobs, two jobs for two tenants run in one
  worker loop. Source: laravel/octane v2.17.5 `src/ApplicationGateway.php`
  `terminate()`, laravel/framework v12.53.0 `src/Illuminate/Routing/Route.php` `flushController()` and
  `src/Illuminate/Queue/QueueServiceProvider.php` reset scope (read 2026-10).
- [invariant] Tenant context is forgotten first, and the flush list holds only the app's own bindings. The
  middleware that binds the tenant starts with `app()->forgetInstance()` for the tenant key and any sub-tenant
  context, before any early return. Jobs that bind tenant context forget it in `finally`. Every key the app
  binds with `app()->instance()` is in `config('octane.flush')`, and nothing else: no framework or package
  managers (social login factory, filesystem, cache, mail, notification, broadcast). Why: `forgetInstance()` on
  a manager drops driver extensions that a package registered once at boot, so the driver fails from the
  second request on, and Octane already resets those managers with its own listeners. Test: a guard in both
  directions (each `->instance('key'` in `app/` is listed in `octane.flush`, and each entry is such a key),
  plus a request as tenant A followed by an unauthenticated request that finds nothing of A bound;
  `scripts/octane_scan.py` reports no OS05, OS08 or OS09 finding.
  Source: laravel/octane v2.17.5 `src/Listeners/FlushTemporaryContainerInstances.php`,
  `GiveNewApplicationInstanceTo*Manager` and `PrepareSocialiteForNextOperation` (read 2026-10).

What each runtime resets, as read in the versions above:

| Runtime | Route's controller instance | Scoped instances | `instance()` bindings, singletons, statics |
|---|---|---|---|
| Octane | dropped after a normally terminated request; kept when a Throwable escapes the gateway, because `terminate()` is skipped (`src/Worker.php`) | flushed | kept, except keys in `octane.flush` and what Octane's listeners reset; an `instance()` written through `app()` during a request lands on the per-request clone and is dropped with it |
| HTTP test client | one instance serves every request in a test; the framework never calls `flushController()` | kept within a test | kept within a test |
| `queue:work` | not applicable | reset before each job | kept; `octane.flush` does not apply |

### Test parity

- [invariant] The full suite runs on PostgreSQL in a blocking CI lane with a dedicated test database, never the
  dev database. A fast SQLite lane may run in addition. Run PostgreSQL-specific code on PostgreSQL before calling
  it done. Why: SQLite hid real defects, among them undefined row order without `ORDER BY` and a caught unique
  violation that aborts the surrounding PostgreSQL transaction. Test: a drift canary file of PostgreSQL-only
  tests (jsonb key order, savepoint or upsert, `timestamptz(0)` rounding, CHECK constraints, aggregate aliases)
  runs in the required lane. Source: https://www.postgresql.org/docs/current/tutorial-transactions.html,
  https://www.postgresql.org/docs/current/datatype-json.html (verified 2026-10).
- [invariant] Tests run on the production PHP minor, declared once in `composer.json` under
  `config.platform.php`. `tests/bootstrap.php` aborts with an actionable message when the running major.minor
  differs. An override variable exists for local runs on another minor and is never set in CI. Why:
  `round(374.49999999999994)` returns 375 on PHP 8.3.10 and 374 on PHP 8.4.27, so a money test was green on one
  minor and red on the other. Test: run the bootstrap under another minor and see it abort.
  Source: https://github.com/php/php-src/blob/PHP-8.4/UPGRADING (round() "pre-rounding" fix, verified 2026-10),
  reproduced on both versions.
- [invariant] The test environment is hermetic, and each pin is proven. Every env value a run depends on
  (database, cache, queue, mail, OAuth client IDs, outbound HTTP, metrics stores, brokers) is pinned, and a test
  asserts that each pin reaches `config()`. Values that must beat the container's environment go in `<server>`
  entries: `<env force="true">` writes only `putenv()` and `$_ENV`, and Laravel's env repository reads `$_SERVER`
  first. Outbound HTTP is blocked with `Http::preventStrayRequests()`, and integration tests against real
  infrastructure are opt-in with their own database. Why: pins that silently did not apply let tests reach
  real credentials and delete rows in a shared dev store. Test: iterate the PHPUnit config's pins and compare
  each with the resolved config. Source: phpunit 12.5.8 `src/TextUI/Configuration/PhpHandler.php`,
  vlucas/phpdotenv v5.6.3 `RepositoryBuilder`, https://docs.phpunit.de/en/12.5/xml-configuration-file.html
  (verified 2026-10).

### Queues

- [invariant] Jobs that wake a person (alerts, escalations, follow-ups) have their own queue and worker, and
  nothing else is dispatched to that queue. A general worker may list it first as a fallback. Its backlog is
  exported as a metric with an alert. Horizon supervisors and separate `queue:work --queue=[name]` processes
  both satisfy this. Why: a Redis-backed queue is FIFO, so a bulk dispatch ahead of a page delays the page, and
  more workers only share the delay. Test: dispatch every wake-up job and assert its queue name; assert the
  queue appears in exactly one dedicated worker definition.
- [invariant] Guards never read asynchronously written data. Dedupe, ownership and "already done" checks read
  columns written in the same request (`created_by`, a unique key, a status column), never a queued audit log or
  another table a job fills. Why: a duplicate guard built on the audit log passed with the sync test queue and
  never fired in production, where the entry arrived seconds later. Test: the guard test runs under
  `Queue::fake()` and asserts that the second attempt is rejected.

### Time and mail

- [invariant] Datetimes are converted to UTC before they reach Eloquent: parse, call `->utc()`, then assign.
  Pin the connection time zone to UTC, and behind a transaction-mode pooler also on the server
  (`ALTER ROLE ... SET timezone = 'UTC'`), because Laravel applies the connection's `timezone` option with a
  `SET` after connecting, and PgBouncer marks `SET` as never compatible with transaction pooling. Why: Eloquent
  formats dates with `Y-m-d H:i:s`, which drops the offset, so `10:00+01:00` is stored as the wall time
  `10:00`. Test: each time-accepting endpoint gets a `+01:00` input test that asserts the stored UTC instant.
  Source: laravel/framework v12.53.0 `HasAttributes::fromDateTime()`, `Grammar::getDateFormat()`,
  `PostgresConnector::configureTimezone()`; https://www.postgresql.org/docs/current/datatype-datetime.html,
  https://www.pgbouncer.org/features.html (verified 2026-10).
- [invariant] When a mailable must use a specific mailer, pin it at the call site with
  `Mail::mailer('[name]')->to($recipient)->send($mailable)`. `Mail::to()->send()` goes through the default
  mailer, whose `sendMailable()` overwrites the mailable's own mailer. Test mail content by rendering it: URLs
  in the text part keep `&` unescaped, and signed links still validate. Why: a deliverability test went out
  through the wrong provider, and text parts that turned `&` into `&amp;` broke signed links, which a fake
  never renders. Test: send through the production call path and assert the mailer name; render each mailable
  with links and validate its signed URLs. Source: laravel/framework v12.53.0 `src/Illuminate/Mail/Mailer.php`
  `sendMailable()`, `src/Illuminate/Mail/Mailable.php` `send()` (read 2026-10).

### Stores

- [default] Valkey or Redis through the PhpRedis extension, with Predis only where the extension cannot be
  installed. Build the extension from a pinned release with a checksum. Queues, sessions and locks never sit on
  an instance whose `maxmemory-policy` evicts keys; that policy is a server setting, so a separate database or
  connection on an evicting instance does not protect them. Give queues and sessions their own connection, so
  clearing the cache cannot wipe them. Trade-off: a compiled extension in the image, and either a second
  instance or a cache without eviction. Deviate only with an ADR that names this trade-off. Proof: a config
  test that `database.redis.client` is `phpredis` and that the queue and session connections differ from the
  cache connection. Source: https://laravel.com/docs/12.x/redis, https://valkey.io/topics/migration/,
  https://valkey.io/topics/lru-cache/ (verified 2026-10).
- [default] Cache entries are tagged by tenant and resource (`tenant:{id}`, `tenant:{id}:projects`), and a write
  flushes the narrowest tag. A value derived from what the current actor may see carries a fingerprint of that
  visible set in its key. Membership and permission caches have one invalidator each. Trade-off: a tag-capable
  store is required, and visibility keys lower the hit rate. Deviate only with an ADR that names this
  trade-off. Proof: two reads around a write differ; two actors with different visibility get different values
  for the same logical key. Source: https://laravel.com/docs/12.x/cache#cache-tags (no tags on the file,
  dynamodb or database drivers, verified 2026-10).
- [default] When the app caches third-party responses, it caches only responses that validate:
  `Cache::rememberWhen()` or `flexibleWhen()` from `rene-roscher/conditional-cache-laravel`, with a validator, a
  `default` for failures, `retryAfter` for controlled negative caching and `lock` against stampedes. Trade-off:
  a package dependency, and a validator per upstream. Deviate only with an ADR that names this trade-off.
  Proof: with `Http::fake()` returning an error payload, the next call fetches again (or returns the default
  within `retryAfter`), and the last good value survives a failed refresh.
  Source: https://github.com/Rene-Roscher/conditional-cache-laravel (README, verified 2026-10).
- [default] When sessions are cache-backed and users need a device list or "log out everywhere", keep the
  session store as the source of truth and add a metadata registry with `rene-roscher/user-sessions-laravel`.
  Point its debounce cache at a shared persistent store, set retention for the registry (it holds IP addresses
  and user agents), and never copy session IDs into logs or job payloads. Trade-off: a registry table and its
  retention job. Deviate only with an ADR that names this trade-off. Proof: N requests within the debounce
  window cause at most one registry write; a revoked device's next request is a guest.
  Source: https://github.com/Rene-Roscher/user-sessions-laravel (README, verified 2026-10).

### Framework guards

- [default] `Model::shouldBeStrict(! app()->isProduction())` is on, and production reports lazy-loading
  violations through `handleLazyLoadingViolationUsing()` instead of throwing. Trade-off: missing eager loads
  and unfillable attributes fail loudly in development and tests. Deviate only with an ADR that names this
  trade-off. Proof: a test asserts `Model::preventsLazyLoading()`, `preventsSilentlyDiscardingAttributes()` and
  `preventsAccessingMissingAttributes()` in the test environment. Source: laravel/framework v12.53.0
  `src/Illuminate/Database/Eloquent/Model.php` (read 2026-10).
- [default] List pages, dashboards and index endpoints have a query budget: an absolute count, and N records
  cost about as much as one. Tests that compare query counts across requests call `freezeTime()` before the
  first request, and the counting helper lives in `tests/Pest.php`. Trade-off: budgets need updating when a
  page legitimately grows. Deviate only with an ADR that names this trade-off. Why: a terminating callback that
  stamps `last_used_at` adds an UPDATE whenever a second boundary passes between requests. Proof: the budget
  tests, and one red run after adding a lazy load.
- [default] Jobs receive scalar IDs plus every business parameter they need (tenant, tax rate, locale), never
  ambient request or container context. Transactional code dispatches with `afterCommit()`. Jobs never depend on
  providers that boot only in the web process, such as an admin panel's URL helpers; deep links come from config.
  Trade-off: longer constructors. Deviate only with an ADR that names this trade-off. Why: a worker has no
  tenant bound, and a job that built URLs through a web-only panel failed in production while passing in tests,
  where every provider boots. Proof: each job is constructed and handled from its constructor arguments alone,
  with web-only providers not registered.

## Procedure

### Fast path

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/octane_scan.py [app root]` (in clients without `CLAUDE_SKILL_DIR`,
   the script is in this skill's `scripts/` folder). It names the tokenizer it used.
2. Exit 1 means a blocker or high finding: stop, fix it, and run the scanner again. If you cannot fix it,
   report the finding with its file, line and rule instead of finishing.
3. Never add an `// octane-scan: allow` comment on your own. Only the code owner may accept a finding, with a
   reason in the comment. Medium and low findings go into the report with your judgement.

### Steps

1. Read `composer.lock` and `composer.json`: framework, Octane, PHPUnit or Pest, PHP platform version. Compare
   with [references/verification-log.md](references/verification-log.md) and re-read the vendor lines for any
   fact whose version differs. If `laravel/boost` is missing from `require-dev`, propose
   `composer require laravel/boost --dev` and `php artisan boost:install`, and wait for approval.
2. When the change touches services, bindings, middleware, controllers or jobs, run the scanner before editing
   and again after (fast path). What each rule detects and misses is in
   [references/long-lived-workers.md](references/long-lived-workers.md).
3. Name the environment differences this change touches, from the meta-rule list.
4. Before changing `octane.flush`, a singleton or a scoped binding, read what the installed Octane version
   already resets ([references/long-lived-workers.md](references/long-lived-workers.md)).
5. Apply the rule and write its guard test ([references/guard-artifacts.md](references/guard-artifacts.md)).
6. Run the change on the production engine and PHP minor: the PostgreSQL lane, in the production-equal
   container. If you cannot run it, say so and give the exact command.
7. Report which lanes ran, which did not, and which facts you re-checked against the installed source.

## Traps

- One controller instance per test. A service injected into the controller constructor keeps its memo across
  every request in a test, so a test shows stale data that Octane would not, or hides a bug that a long-lived
  kernel would show.
- Flushing a manager to "fix" Octane. It breaks package-registered drivers from the second request. Read the
  installed listeners first, and treat a bug report cited without a link as unverified.
- A forced `<env>` that loses to the container. Prove pins with a test instead of trusting the XML.
- The sync queue in tests runs jobs inline, so anything that reads job output looks immediate.
- Query counts that flake. An unfrozen clock lets a once-per-second write land between two requests.
- `Mail::fake()` never renders a template, so escaping and broken signed links pass.
- `pluck(DB::raw('count(*)'))`: PostgreSQL names the column `count`, SQLite names it `count(*)`. Alias every raw
  expression (`selectRaw('count(*) as total')`).
- A job that passes in tests because the test process boots every provider, including ones that production
  queue workers never boot.

## Done when

- `scripts/octane_scan.py` exits 0 on the app, with no allow comment added in this change, and the report
  names the tokenizer mode and any medium findings in touched files.
- Every stateful service touched has a two-requests-in-one-test regression test, and the flush guard passes in
  both directions.
- The change ran on the PostgreSQL lane and on the production PHP minor, or the report says it did not and why.
- New env pins have a test that proves they reach `config()`.
- New wake-up jobs are on the dedicated queue, asserted by a test.
- Time-accepting endpoints touched have a `+01:00` test; mailables touched have a rendered test.
- Version-bound facts used were re-checked against the installed source, or marked unverified.

## References

- [references/long-lived-workers.md](references/long-lived-workers.md): load when touching Octane, FrankenPHP
  worker mode, queue workers, singletons, scoped bindings, the flush list or memo services, auditing an area
  for long-lived worker safety, or reading an `octane_scan.py` finding.
- [scripts/octane_scan.py](scripts/octane_scan.py): run before and after changing services, bindings,
  middleware, controllers or jobs; `--self-test` checks it offline against its fixtures.
- [references/postgres-parity.md](references/postgres-parity.md): load when writing migrations, upserts, JSON
  columns, timestamps or aggregates, or setting up the PostgreSQL CI lane.
- [references/test-environment-parity.md](references/test-environment-parity.md): load when editing PHPUnit
  config, env pins, the runtime-minor guard or production boot defaults, or when CI and local results differ.
- [references/queues.md](references/queues.md): load when adding a job, choosing a queue, isolating wake-up
  jobs, or setting `retry_after` and timeouts.
- [references/valkey-cache-sessions.md](references/valkey-cache-sessions.md): load when configuring Redis or
  Valkey, tiers, cache tags, conditional caching, sessions or device management.
- [references/mail-and-time.md](references/mail-and-time.md): load when writing mailables, choosing mailers,
  handling datetime input, time zones or poolers.
- [references/verification-log.md](references/verification-log.md): load before relying on a version-bound
  fact; it lists each fact with its file and the version it was checked at.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when setting up the guard tests in a
  project, or checking which exist.

## Sources

- https://www.postgresql.org/docs/current/tutorial-transactions.html, https://www.postgresql.org/docs/current/sql-savepoint.html:
  an aborted transaction block regains control only with `ROLLBACK` or `ROLLBACK TO`. Verified 2026-10.
- https://www.postgresql.org/docs/current/datatype-json.html: jsonb keeps neither key order nor duplicate keys.
  Verified 2026-10.
- https://www.postgresql.org/docs/current/datatype-datetime.html: input without a zone is read in the
  `TimeZone` setting; values are stored as UTC. Verified 2026-10.
- https://www.postgresql.org/docs/current/sql-alterrole.html: `ALTER ROLE ... SET` sets the session default
  at login. Verified 2026-10.
- https://www.pgbouncer.org/features.html: `SET`/`RESET` never compatible with transaction pooling. Verified
  2026-10.
- https://github.com/php/php-src/blob/PHP-8.4/UPGRADING: round() pre-rounding removed in PHP 8.4. Verified
  2026-10.
- https://docs.phpunit.de/en/12.5/xml-configuration-file.html: `<env>` sets `$_ENV`; `force` overwrites
  existing values. Verified 2026-10.
- https://laravel.com/docs/12.x/redis, https://laravel.com/docs/12.x/cache, https://laravel.com/docs/12.x/horizon
  and https://valkey.io/topics/migration/: PhpRedis recommendation, tag support per driver, Horizon's Redis
  requirement, Valkey compatibility with Redis OSS 7.2 and earlier. Verified 2026-10.
- https://github.com/Rene-Roscher/conditional-cache-laravel and
  https://github.com/Rene-Roscher/user-sessions-laravel: package behaviour and requirements. Verified 2026-10.
- https://laravel.com/docs/12.x/boost: installing Laravel Boost. Verified 2026-10.
- https://laravel.com/docs/12.x/octane#dependency-injection-and-octane: do not inject the container, request or
  configuration repository into singleton constructors; a resolver closure or per-call argument is the fix.
  Verified 2026-11.
