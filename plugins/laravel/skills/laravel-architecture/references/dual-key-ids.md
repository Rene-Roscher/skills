# Dual-key IDs in Laravel

Load when adding a model, migration, route binding, resource or cursor-paginated endpoint, or when choosing an
ID format. `dual-key-identifiers` holds the stack-neutral rule. This file is the Laravel wiring.

## Contents

- The two keys
- One helper, one trait
- Resources and props
- Route binding and scoping
- Cursor pagination
- Shape validation
- Choosing another format

## The two keys

- Internal: the `bigint` primary key from `$table->id()`. Joins and foreign keys use it. It is never serialized.
- External: a fixed-length string column with a unique index, for example `public_id` of length 21. Check that
  the column compares case-sensitively, because the alphabet has both cases.
- Add the external column in the same migration that creates the table. Backfilling it later needs a data
  migration and a `NOT NULL` step after the backfill.
- Internal pivot tables and rows that never leave the server get no external column.

## One helper, one trait

One class defines length, alphabet, generator and the validation pattern. Everything else calls it.

```php
final class PublicId
{
    public const LENGTH = 21;
    public const ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    public const PATTERN = '/^[0-9A-Za-z]{21}$/'; // widen it if an older, larger alphabet exists

    public static function generate(): string
    {
        $id = '';
        while (strlen($id) < self::LENGTH) {
            foreach (str_split(random_bytes(32)) as $byte) {
                $value = ord($byte) & 63;   // uniform over 0..63
                if ($value < 62) {          // reject 62 and 63, so no value is favoured
                    $id .= self::ALPHABET[$value];
                    if (strlen($id) === self::LENGTH) {
                        break;
                    }
                }
            }
        }

        return $id;
    }
}
```

The trait fills the column on `creating` and makes route binding use it:

```php
trait HasPublicId
{
    public static function bootHasPublicId(): void
    {
        static::creating(function (Model $model): void {
            $model->public_id ??= PublicId::generate();
        });
    }

    public function getRouteKeyName(): string
    {
        return 'public_id';
    }
}
```

If the project wraps an ID library instead, read its source at the locked version and call its secure mode.
`hidehalo/nanoid-php` 2.0 is one example: `generateId()` defaults to a mode built on `mt_rand()`.

Entropy: 21 characters from 62 symbols give 21 × log2 62, about 125 bits.

## Resources and props

- Resources map `'id' => $this->public_id`. A related record appears as its external ID, either nested
  (`'owner' => ['id' => $this->owner->public_id]`) or as a key whose value is the external ID.
- Inertia props are built from resources or explicit arrays. Passing `$model->toArray()` into props serializes
  `id` and every foreign key column.
- Adding `id` and foreign keys to the model's `$hidden` is a second line of defence. It does not replace the
  mapping, because code that reads attributes directly bypasses it.

## Route binding and scoping

- With the trait, `{project}` binds by the external column.
- Nested routes: `{task:public_id}` under `{project}` scopes the child through the parent's relation, and
  `->scopeBindings()` scopes it even without a custom key (Laravel 13.x routing docs, via Context7,
  2026-10-31). Check the docs for the installed major.
- Top-level tenant-owned records are resolved through the tenant:
  `$tenant->projects()->where('public_id', $id)->firstOrFail()`. A foreign ID and a missing ID both give 404.
- Binding finds a record. Policies still decide access.

## Cursor pagination

Laravel's cursor is base64url-encoded JSON of the order-by values of the boundary row
(`Illuminate\Pagination\Cursor::encode()`, framework v12.53.0). A cursor over `id` exposes the internal key.
Order by a timestamp plus the external ID as tie-breaker. Offset pagination (`?page=2`) reveals no key.

## Shape validation

Validate the shape in FormRequests and route constraints so malformed input fails fast. Shape never decides
existence or tenant; the scoped lookup does. When the alphabet is tightened, keep the pattern accepting the old
alphabet so old links still resolve.

## Choosing another format

The default is NanoID (see SKILL.md). A different format needs an ADR that states the trade-off:

| Format | Layout | Index on insert | Reveals |
|---|---|---|---|
| NanoID, 21 of 62 | random, about 125 bits | scattered | nothing |
| UUIDv4 | 122 random bits | scattered (RFC 9562, 2.1) | nothing |
| UUIDv7 | 48-bit Unix milliseconds first (RFC 9562, 5.7) | in order (RFC 9562, 6.11) | creation time |
| ULID | 48-bit milliseconds, then 80 random bits, 26 characters | in order | creation time |

Whatever the format, possession of an ID grants nothing. RFC 9562 section 8 says UUIDs must not be used as
security capabilities. Authorization runs on every request.

Sources: https://www.rfc-editor.org/rfc/rfc9562.html, https://github.com/ulid/spec,
https://laravel.com/docs/13.x/routing (all verified 2026-10).
