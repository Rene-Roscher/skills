# Logging and error trackers

Settings move between SDK versions. Read the installed version from the lockfile and check that version's docs
before you write a config key. Dates below are when the setting was checked.

## PHP runtime

| Setting | Effect | Source |
|---|---|---|
| `zend.exception_ignore_args=On` | "Excludes arguments from stack traces generated from exceptions." Default `0` when no php.ini is loaded; available since PHP 7.4 | https://www.php.net/manual/en/ini.core.php (verified 2026-10) |
| `#[\SensitiveParameter]` | marks a parameter "that is sensitive and should have its value redacted if present in a stack trace"; PHP 8.2 and later | https://www.php.net/manual/en/class.sensitiveparameter.php (verified 2026-10) |

Check the production image, not the developer machine: `php -r 'exit(ini_get("zend.exception_ignore_args") ? 0 : 1);'`.

## Sentry PHP and Sentry Laravel (checked 2026-10-31)

Sources: https://docs.sentry.io/platforms/php/data-management/data-collection/,
https://docs.sentry.io/platforms/php/configuration/options/,
https://docs.sentry.io/platforms/php/guides/laravel/configuration/options/.

- Local variables are sent with unhandled errors. `stack_frame_variables` controls this and defaults to `true`.
  `zend.exception_ignore_args=1` prevents PHP from providing variables to the SDK regardless of that option.
- Without `data_collection`, the SDK collects conservatively and `send_default_pii` keeps working. Keep it
  `false`.
- Passing a `data_collection` array opts into its defaults for every key you do not set. Those defaults are more
  permissive: the logged-in user, cookies, request and response bodies (and on Laravel, SQL bindings). If both are
  set, `send_default_pii` is ignored. Either set every key explicitly or leave `data_collection` out.
- The first version with `data_collection` differs between pages: 4.29.0 on the Laravel guide, 4.33.0 on the
  PHP page. Confirm against the changelog of the package in your lockfile.
- `before_send` runs on every event. Scrub there: authorization headers, cookies, query strings with tokens,
  request bodies, and any key on your own denylist.
- Built-in scrubbing matches key names (`auth`, `token`, `password` and similar). A token under an unusual key,
  or inside a free-text message, passes through.

## Other trackers

The same questions apply to any SDK: are local variables or arguments sent, are request bodies sent, is user
identity attached, which hook scrubs events before sending. Look them up per SDK and version; do not assume the
Sentry answers carry over.

## Log lines

- IP addresses: mask before writing (for example /24 for IPv4, /48 for IPv6) unless a documented purpose needs
  the full address, with its own retention.
- Tokens: log a short prefix of a hash (for example 8 hex characters of SHA-256) so two lines can be correlated.
  Never the token, never the full hash: an unsalted full hash is a lookup key for the token.
- Free text from customers or their systems: treat it as personal data. Log its length or a classification,
  not the text.
- Exception messages from libraries can contain URLs with credentials, SQL with values, or response bodies.
  Log them only to a restricted sink with short retention, never to a customer-visible surface.

## Errors shown to people and systems

- Browsers, API clients, workers, delivery logs and CSV error reports get a curated message from a typed domain
  exception, plus a correlation ID.
- The raw exception goes to the error tracker only, after scrubbing.

## Where the tracker sits in the paperwork

- A hosted error tracker is a recipient of processor data (customer payloads in traces) and controller data
  (your users' IPs): subprocessor list, AVV annex, privacy notice, transfer check.
- A self-hosted tracker is not a subprocessor, but it is a system with personal data: VVT entry, retention,
  access control in the TOM.
