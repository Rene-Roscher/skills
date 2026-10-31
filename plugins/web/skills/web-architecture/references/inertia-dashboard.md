# Inertia dashboard

Decisions for authenticated dashboards built with Inertia and Vue. Syntax is in the Inertia docs
(https://inertiajs.com, verified 2026-10-31); check the pages for your installed major version.

## SSR off

- Set SSR off explicitly in `config/inertia.php` (`ssr.enabled`), and do not build an SSR bundle for the
  dashboard. The current Inertia docs also turn SSR off in the Vite plugin; follow the steps for your version.
- Inertia falls back to client rendering when SSR fails, without an error. A half-enabled setup therefore costs
  an SSR request per page view and nobody notices it failing.
- If a public Inertia page must be indexed and SSR is turned on for it: run the SSR server as its own process
  with a health check and monitoring, and make SSR errors visible. The current docs describe a
  `throw_on_error` option for that; confirm it exists in your installed adapter before relying on it.

Config test (Pest sketch):

```php
it('keeps SSR off for the dashboard', function () {
    expect(config('inertia.ssr.enabled'))->toBeFalse();
});
```

## Data loading

- Refresh server state with partial reloads that name the props they need (`only`), not full reloads.
- Polling uses the Inertia polling helper with `only`, at an interval that matches how fast the data changes.
  Stop polling when the tab is hidden if the helper supports it.
- A realtime event (WebSocket) triggers a partial reload of the affected props. Do not patch client state from
  the event payload; the server stays the source of truth. Debounce bursts of events into one reload.
- Keep shared props small. Large or slow props are loaded lazily or deferred.

## JSON calls outside Inertia visits

One fetch wrapper for every non-Inertia request:

- sends `Accept: application/json` and `X-Requested-With: XMLHttpRequest`, so the backend answers errors with
  JSON instead of an HTML redirect;
- reads the CSRF token from the `XSRF-TOKEN` cookie and sends it as `X-XSRF-TOKEN`
  (https://laravel.com/docs/12.x/csrf#csrf-x-xsrf-token, verified 2026-10-31);
- throws on any non-2xx status, so a 419 or 422 cannot be read as success;
- builds the URL from a generated route helper.

## Tenant switch

Persistent layouts survive navigation. On a tenant switch:

- module-level caches drop the previous tenant's data before the new fetch starts;
- realtime channels for the old tenant are left and the new tenant's channels joined;
- polling restarts for the new tenant.

A unit test switches tenant and asserts the cache is empty before the new fetch resolves.

## Permissions in the UI

Page props may carry the user's abilities to hide buttons and menu entries. That is presentation. The server
authorizes every action, and the tests for it call the server (`authorization-rbac`).
