# Mail and time

Load when writing mailables, choosing mailers, handling datetime input, or configuring time zones and poolers.
Facts read in laravel/framework v12.53.0 on 2026-10-31.

## Contents

- Mailer selection
- Rendered mail tests
- Datetime input
- Connection time zone and poolers
- Mutable dates

## Mailer selection

- `Mail::to($user)->send($mailable)` resolves the default mailer. `Mailer::sendMailable()` then calls
  `$mailable->mailer($this->name)`, which overwrites the mailer set on the mailable
  (`src/Illuminate/Mail/Mailer.php`).
- `Mailable::send()` honours the mailable's own mailer only when it receives the mail factory
  (`src/Illuminate/Mail/Mailable.php`).
- So pin the mailer at the call site: `Mail::mailer('transactional')->to($user)->send($mailable)`.

Test: send through the same call path production uses and assert the mailer or transport name.

## Rendered mail tests

`Mail::fake()` records that a mailable was sent. It never renders the template. Render each mailable that
contains links:

- Blade `{{ }}` echoes pass through `htmlspecialchars` (https://laravel.com/docs/13.x/blade, via Context7,
  2026-10-31). In a plain-text view that turns `&` in a URL into `&amp;`, and a signed URL stops validating.
  In text views, print URLs with `{!! $url !!}`.
- Assert that every URL in the text part contains no `&amp;`, and that each signed URL passes signature
  validation.
- Render each locale the app sends.

## Datetime input

Eloquent stores dates through `fromDateTime()`, which formats with `getDateFormat()`. The base grammar returns
`Y-m-d H:i:s` (`HasAttributes.php`, `Database/Grammar.php`). The offset is dropped: `10:00+01:00` is written as
`10:00`. PostgreSQL reads a literal without a zone in the session `TimeZone` and stores UTC
(https://www.postgresql.org/docs/current/datatype-datetime.html).

- Parse, convert, assign: `Carbon::parse($input)->utc()`, in the FormRequest's `validated()` handling or the DTO
  factory, before the model sees it.
- A model `$dateFormat` or a custom cast changes this path. Check both before assuming the default.
- Test every time-accepting endpoint with a `+01:00` input and assert the stored UTC instant. Tests that only
  send UTC never see the bug.

## Connection time zone and poolers

- Pin the connection's `timezone` option to UTC. Laravel's PostgreSQL connector applies it with a
  `set time zone` statement after connecting (`PostgresConnector::configureTimezone()`).
- Behind PgBouncer in transaction mode, `SET` is never compatible (https://www.pgbouncer.org/features.html), so
  a later transaction can run on a server connection with another time zone. Set it on the server as well:
  `ALTER ROLE app_user SET timezone = 'UTC'`, which becomes the session default at login
  (https://www.postgresql.org/docs/current/sql-alterrole.html). PgBouncer tracks `TimeZone` as a startup
  parameter, so passing it at connect time also works.
- Config test: the connection's `timezone` is UTC. Infrastructure check: the role default.

## Mutable dates

`Date::use(CarbonImmutable::class)` at boot. With mutable dates, `$booking->starts_at->addDay()` changes the
instance in place, and every other reference to it moves too.
