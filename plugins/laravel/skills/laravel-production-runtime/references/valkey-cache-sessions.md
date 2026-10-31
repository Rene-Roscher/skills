# Valkey, cache and sessions

Load when configuring Redis or Valkey, durability tiers, cache tags, conditional caching, sessions or device
management. Syntax: https://laravel.com/docs/12.x/redis, https://laravel.com/docs/12.x/cache,
https://laravel.com/docs/12.x/session.

## Contents

- Client
- Tiers
- Tagged cache
- Validated caching of third-party responses
- Sessions and device management

## Client

- The Laravel docs encourage the PhpRedis extension for performance and name Predis as the option when the
  extension cannot be installed (https://laravel.com/docs/12.x/redis, via Context7, 2026-10-31).
- Valkey is compatible with Redis OSS 7.2 and earlier, and existing Redis clients connect without code changes.
  Data files from Redis Community Edition 7.4 and later are not compatible
  (https://valkey.io/topics/migration/, 2026-10-31).
- Build the extension in the image from a pinned release with a checksum. A package registry that fails during
  the image build blocks every release until it recovers.
- Check the PhpRedis release notes against the Valkey version for features you use beyond plain commands
  (Lua scripts, client-side caching).

## Tiers

| Tier | Holds | Eviction | Persistence |
|---|---|---|---|
| volatile | cache, rate limits | allowed (`allkeys-lru` or similar) | optional |
| durable | queues, sessions, locks | `noeviction` | on |

An evicting instance silently drops queued jobs and logs users out under memory pressure. `maxmemory-policy`
is a server setting (`valkey.conf` or `CONFIG SET`), so it applies to every database on the instance. A
separate database or connection for queues on an `allkeys-lru` instance does not protect them, and
`volatile-*` policies still evict sessions, because session keys carry a TTL
(https://valkey.io/topics/lru-cache/, 2026-10-31). Two ways that hold: one instance per tier, or one
`noeviction` instance where cache writes fail when memory is full. Separate connections are still needed, so
that clearing the cache cannot wipe queues or sessions.

Config test: the queue and session connections differ from the cache connection, and `database.redis.client`
is `phpredis`. The `maxmemory-policy` check per instance belongs to the infrastructure repository.

## Tagged cache

- Tags are not supported by the file, dynamodb and database drivers (https://laravel.com/docs/12.x/cache).
- Tag by tenant and by resource: `tenant:{id}`, `tenant:{id}:projects`. A write flushes the narrowest tag that
  covers it.
- A value derived from what the actor may see (filtered lists, counts, dashboards) carries a fingerprint of
  the visible set in its key, for example a hash of the role's permission version plus the actor's scope.
  Restricted members inside one tenant otherwise get an admin's cached view.
- Membership and permission caches have one invalidator each, called from every write path that changes them.

Tests: two reads around a write differ; two actors with different visibility get different values for the same
logical key.

## Validated caching of third-party responses

`Cache::remember()` stores whatever comes back, including an empty array or an error payload, for the whole
TTL. A failed background refresh with `flexible()` can replace the last good value with a broken one.
`rene-roscher/conditional-cache-laravel` adds `Cache::rememberWhen()` and `flexibleWhen()`
(https://github.com/Rene-Roscher/conditional-cache-laravel, README read 2026-10-31):

- A validator decides whether a result is cached. The README documents the default and shows `filled(...)`.
- `default` is returned when the result fails validation.
- `retryAfter` returns the default for that many seconds before calling the upstream again. It requires a
  `default`.
- `lock` (seconds) lets one process compute while others wait. It needs a lock-capable store.
- `flexibleWhen()` uses the same keys and lock as `Cache::flexible()`.
- Requires PHP 8.2+ and Laravel 11.24+, 12 or 13.

Tests with `Http::fake()` returning an error payload: the next call fetches again, or returns the default
within `retryAfter`; the last good value survives a failed refresh.

## Sessions and device management

Keep the cache-backed session driver on the durable tier. For a device list and "log out everywhere", use
`rene-roscher/user-sessions-laravel` (https://github.com/Rene-Roscher/user-sessions-laravel, README read
2026-10-31) instead of switching to the database session driver:

- The session store stays the source of truth. A registry table holds metadata only, and revocation ends the
  session in the store, for any session driver.
- Writes are debounced. The debounce needs a shared, persistent cache store, never `array` or `null` outside
  tests.
- Guests are never tracked. Tracking is skipped while an admin impersonates a user.
- Bulk revoke throws `CouldNotRevokeSessions` when any session could not be ended.
- Payloads and job context use the registry row's ULID, never the session ID, which is a bearer credential.
- Requires PHP 8.2 to 8.4 and Laravel 12 or 13.

The registry stores IP addresses and user agents. Set `prune_after_days`, schedule `model:prune`, and list the
registry in the records of processing (`gdpr-engineering`).

Tests: N requests within the debounce window cause at most one registry write; a revoked device's next request
is a guest; a config check that the debounce store is not `array` or `null` outside tests.
