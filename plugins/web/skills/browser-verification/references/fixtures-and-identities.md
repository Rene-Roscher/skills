# Fixtures and identities

Each browser test owns its data and its user. Nothing it does reaches a real person or a shared database.

## The suite's own environment

The suite never shares a process, a port, a database or a build with the developer's running stack.

| Part | Developer stack | Browser suite |
|---|---|---|
| App server | its usual port | its own port, started by the runner (`webServer` with `reuseExistingServer: false`) |
| Asset build | dev server, hot file present | production build into its own output directory; setup fails if the hot file exists |
| Database | dev database | its own database, created and migrated by global setup |
| Cache, sessions, queues | dev stores | stores in the suite's database or its own Redis database number |
| Mail, SMS, webhooks | whatever dev uses | fakes only (see "Side effects") |

Global setup, every run, before the first test:

1. Create or reset the suite's database (fresh schema, seed).
2. Clear the cache store the app uses. Rate-limit counters live there: in Laravel the limiter uses the default
   cache store unless a `limiter` store is configured (https://laravel.com/docs/12.x/rate-limiting, verified
   2026-11-05), and a database cache survives between runs.
3. Read every limit a test can hit (creates per hour, login attempts, invites per day) from the environment, and
   set test values in the suite's environment file, so a full run never meets a production limit. A dedicated
   test that proves the limit sets it low on purpose.
4. Fail loudly when a guard trips: the dev server's port answers on the suite's URL, the hot file exists, or the
   database name is not the suite's.

Proof: run the full suite twice in a row while the dev stack runs. Both runs pass, and the dev database's row counts
are unchanged.

## Creating the tenant and user

- Use the application's real creation path: the signup action or service, or factories that call it. Raw
  inserts skip the side effects a real account has (default settings, roles, a first project) and the page
  then renders a state no user ever sees.
- One tenant per test, or per test file with a unique name. Never reuse a tenant another test mutates.
- Pass every gate a real user passes: terms accepted, onboarding finished, welcome dialogs and product tours
  dismissed, announcements marked seen. Set those flags through the same code path the UI uses. A gate dialog
  left open dims the page and every colour measurement taken behind it is wrong.

## Sessions

- Playwright: log in once in a setup project through the real login form, save `storageState` to a gitignored
  file, and reuse it in the dependent projects. One state file per role (owner, restricted member).
- Pest browser plugin: authenticate the way the project's feature tests do and check the plugin docs for how
  the session reaches the browser (https://pestphp.com/docs/browser-testing).
- Never import cookies or a profile from the user's own browser.

## Locale and theme

- Pin the locale per test. Wording and decimal separators change with it. Set it on the user record when the
  app reads it from there, and in the browser as well (Playwright's `locale` context option, Pest's
  `withLocale`, verified in the Pest docs 2026-10-31).
- Dark mode follows the app's own persistence. If the app stores the theme in a cookie or `localStorage`, set
  that before navigation (`addInitScript` or the stored state). Emulating `prefers-color-scheme` alone
  (Playwright `colorScheme`, Pest `inDarkMode()`) only covers apps that read the media query.
- Record the locale and theme in the report.

## Side effects

- Mail, SMS, chat, push and outgoing webhooks are faked or sandboxed in the test environment. A test asserts it:

```php
it('runs browser tests without real transports', function () {
    expect(config('mail.default'))->toBeIn(['array', 'log']);
    expect(config('services.sms.driver'))->toBe('fake');   // adapt to the project's config keys
});
```

- Payment providers run in their test mode with test keys only.
- A flow that would notify a real person in production is tested against the fake, and the test asserts what
  the fake received.

## Cleanup

- When the browser talks to a server running in another process, a transaction rollback in the test process
  does not undo that server's writes. Use per-test tenants with an explicit teardown, or reset the test
  database between runs.
- Never run browser tests against a shared development database with ad-hoc users, and never against
  production data. A shared database needs backups and restores around every run, and one forgotten restore
  leaves broken data for everyone.

## Client-side storage checks

When a test covers storage, assert the exact key allowlist of what the app stored (`localStorage`,
`sessionStorage`, IndexedDB names, cookies set by script), with no tokens or passwords among them, and that an
aborted flow leaves nothing behind.
