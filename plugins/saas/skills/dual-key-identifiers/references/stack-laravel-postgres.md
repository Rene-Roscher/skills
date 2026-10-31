# Laravel and PostgreSQL notes

Load when the project uses Laravel or PostgreSQL. Facts below were read from laravel/framework source on the `12.x`
and `13.x` branches and the Laravel 12 docs on 2026-10-31. Re-read them for the installed version before relying on
them. The in-suite leak guard for Laravel (middleware, `fail`/`report`/`off` modes, base `TestCase` hook) belongs
to the `laravel-architecture` skill.

## Built-in UUID and ULID traits

- `HasUuids::newUniqueId()` returns `Str::uuid7()` on `12.x` and `13.x`: time-ordered.
  (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Database/Eloquent/Concerns/HasUuids.php)
- `HasVersion4Uuids::newUniqueId()` returns `Str::orderedUuid()`, whose docblock reads "Generate a time-ordered
  UUID". It is a timestamp-first COMB UUID, so it also reveals creation time. The Laravel 12 upgrade guide calls it
  "ordered UUIDv4". (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Database/Eloquent/Concerns/HasVersion4Uuids.php,
  https://laravel.com/docs/12.x/upgrade)
- `Str::uuid()` returns `Uuid::uuid4()`: random. Override `newUniqueId()` with it if an ADR picked UUIDv4.
- `HasUniqueStringIds::uniqueIds()` returns the primary key name by default, and the trait then reports the key type
  as `string` and turns off incrementing. Used as-is, the trait replaces the bigint key, which gives up the two-key
  design. Point `uniqueIds()` at `public_id` if you use the trait at all.
  (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Database/Eloquent/Concerns/HasUniqueStringIds.php)
- For a route field listed in `uniqueIds()`, `resolveRouteBindingQuery()` checks the shape and throws
  `ModelNotFoundException` (404) for an invalid value. A custom trait has to do the same itself.

## A small public-ID trait

The default NanoID needs no package: one class with `random_int(0, 61)` per character over `0-9a-zA-Z` is uniform
and uses the CSPRNG. The trait around it:

- fills `public_id` in the `creating` model event when it is empty;
- returns `public_id` from `getRouteKeyName()`;
- checks the shape in route binding and throws `ModelNotFoundException` for a malformed value;
- keeps `public_id` out of `$fillable` (or in `$guarded`). The creating hook only fills an empty value, so a
  mass-assignable column would let request input win.

## Migrations

- `$table->id()` creates the bigint identity key. Foreign keys use `foreignId()` and point at it.
- `$table->string('public_id', 21)->unique()` and nothing else on that column. Do not add `->index()` as well.
- The alphabet is case-sensitive. Check that the column's collation compares case-sensitively on the engine in use;
  PostgreSQL's deterministic default collations do.

## API Resources and page props

- `'id' => $this->public_id`, and each reference as the related model's `public_id`. Eager-load the relations the
  resource reads, or the translation turns into one query per row.
- Do not pass models straight to page props and rely on `$hidden`. Pass resources or explicit arrays.
- Inertia renders props into the `data-page` attribute, so they are part of what the guard must scan.

## Route binding

- Tenant-owned resources resolve through the tenant. For nested parameters, `scopeBindings()` scopes the child to
  the parent (https://laravel.com/docs/12.x/routing, verified 2026-10-31). Scoping constrains resolution; it does
  not authorize the parent. See `tenant-isolation`.

## Cursor pagination

- `Cursor::encode()` is `base64_encode(json_encode($this->toArray()))` with `+/=` replaced for URLs
  (https://github.com/laravel/framework/blob/12.x/src/Illuminate/Pagination/Cursor.php). Ordering by `id` puts the
  internal key into every `next_cursor`.
- Order by `created_at` and then `public_id` before `cursorPaginate()`.

## Broadcasting

- Name private channels by public ID, for example `invoices.{publicId}`. The channel name appears in the browser's
  network log.

## PostgreSQL schema checks

- Duplicate indexes: the query in `guard-artifacts.md` (same skill).
- Foreign keys are bigint: query `information_schema.columns` joined to the foreign-key constraints, fail CI on any
  other type.
