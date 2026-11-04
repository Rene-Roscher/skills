# Backend feedback, locale resolution and async messages

## Contents

- Error and status responses
- Validation
- Locale resolution
- Queued mail and notifications
- Exports and PDFs
- Formatting on the server

## Error and status responses

- The response carries a stable code and the parameters a sentence needs, for example
  `{ "code": "certificate.expired", "params": { "domain": "example.com", "days": 3 } }`, inside the error
  envelope the API already uses (RFC 9457 problem details in `api-contract`: the code maps to `type` or to an
  extension member).
- The frontend renders its own translated sentence from code and parameters. If the backend also sends a
  message, it renders it in the requesting user's locale (the resolved locale below), and the frontend may still
  prefer its own text.
- Unexpected exceptions map to one generic translated text and a request ID. The exception message goes to the
  log, not into the response, a flash message or a toast.
- Domain exceptions that are meant for users carry a translation key and parameters, not English prose:
  `throw new CertificateExpired(key: 'certificates.errors.expired', params: [...])`, rendered with `__()` at the
  edge.
- Toasts and flash messages take a key: `toast.error(t('servers.delete_failed'))`, `->with('error',
  __('servers.delete_failed'))`. A toast that prints `error.message` shows whatever the server or browser wrote.

## Validation

- Field names in messages come from the translated attribute list (`lang/xx/validation.php`, `attributes`), so
  German users read "Die E-Mail-Adresse ist ungültig." instead of "Das email ist ungültig.".
- Custom rule messages are translation keys with placeholders, not literals in the rule class.
- The API validation error lists the field pointer and a code per error in addition to the message, so clients
  can render their own text.

Source: https://laravel.com/docs/12.x/validation#specifying-attribute-in-language-files (verified 2026-11-04).

## Locale resolution

- One resolver, called by web middleware, API middleware, queued jobs and scheduled commands. Default order: the
  user's saved locale, then the best supported match from `Accept-Language`, then the app default.
- Store the resolved locale on the user at signup, and let the user change it; do not re-read the browser header
  on every request once a setting exists.
- Only supported locales leave the resolver. An unsupported header value falls through to the default.
- Public pages that are cached carry the locale in the URL (see `web-architecture`); the header must not change
  the cached body.
- The header can carry a user's full language preferences; RFC 9110 notes this may be "contrary to the privacy
  expectations of the user". Use it to pick a locale, do not store it.

Source: https://www.rfc-editor.org/rfc/rfc9110.html#name-accept-language (verified 2026-11-04).

## Queued mail and notifications

- Laravel: a notifiable model that implements `HasLocalePreference` is mailed and notified in
  `preferredLocale()`; `Mail::to($user)->locale('en')` and `$user->notify((new InvoicePaid($invoice))->locale('en'))`
  set it per send, and the docs state the locale is remembered when the mail is queued.
- A mail to an address without a user account (invitation, subscriber) stores the locale next to the address and
  passes it on send.
- A job that renders text (export, report, PDF, digest) receives the locale as a constructor parameter, sets it
  for its work and restores it after; see `laravel-production-runtime` for job parameters.
- Subject lines, preheaders, button labels and plain-text parts are translated together with the HTML body.
- Test: render the queued mail for a recipient with another locale than the request's and assert on the subject
  and one body sentence.

Sources: https://laravel.com/docs/12.x/mail#localizing-mailables,
https://laravel.com/docs/12.x/notifications#localizing-notifications (verified 2026-11-04).

## Exports and PDFs

- Human-readable reports (PDF, spreadsheet meant to be read) use the recipient's locale for headings, number and
  date formats, and state the time zone used.
- Machine-readable exports keep stable column keys and ISO 8601 dates with offset, documented once; translating
  them breaks imports on the other side.
- Money in exports carries the currency code in its own column or in the formatted value.

## Formatting on the server

- Laravel `Number::format($value, locale: 'de')` and `Number::currency($value, in: 'EUR', locale: 'de')` give
  "100.000" and "1.000,00 €"; pass the resolved locale, not the app default.
- Dates: convert to the user's time zone before formatting, and format with the locale (for example Carbon's
  `locale()` with `isoFormat()`); never build "d.m.Y" by hand for one language.
- Durations: `Intl.DurationFormat` in the browser reached Baseline in 2025 and may be missing on older devices;
  otherwise use one plural message per unit.

Sources: https://laravel.com/docs/12.x/helpers#method-number-format (verified 2026-11-04 through a documentation
index tool, Context7); https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat
(verified 2026-11-04). Carbon `isoFormat()` is named from practice and not verified here.
