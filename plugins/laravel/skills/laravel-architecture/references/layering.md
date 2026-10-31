# Layering

Load when placing new code, splitting a large controller or service provider, or choosing between service,
action and DTO. Examples use an invoicing domain.

## Where code goes

| Concern | Home | Note |
|---|---|---|
| Input shape and "may this user send this request" | FormRequest | `authorize()` and `rules()`; scoped `exists` for referenced IDs |
| One use case that writes | Service with one entry method | transaction, audit, events, plan or budget checks |
| A step several services share | Action | single purpose, no HTTP types |
| Data crossing a boundary | `final readonly` DTO | service input, job payload description, vendor response mapping |
| Closed value set | string-backed enum | mirrored by a CHECK constraint |
| Reads, lists, reports | `...Query` or `...Reader` | may have several public methods |
| Output shape | API resource or props builder | external IDs only |
| Access decision on a record | Policy | binding does not authorize |
| Vendor call | adapter behind a domain interface | see `vendor-boundaries.md` in this folder |
| Work after commit | job or listener | explicit parameters (`laravel-production-runtime`) |

## Service, action or DTO

- Start with the service. Extract an action when a second service needs the same step, not before.
- A service takes a DTO or scalars, never the `Request`. That keeps it callable from the API, a job, a console
  command and a test.
- A service validates nothing that the FormRequest already validated, but it enforces business rules that
  hold for every caller (limits, state transitions).
- A DTO has no behaviour beyond construction helpers such as `fromArray()` or `fromValidated()`.

## One write path for UI and API

The web controller and the API controller call the same service with the same DTO. A parity test pins it:

1. Create two fresh tenants through the real tenant-creation action.
2. Send the same input through the web route for one and the API route for the other.
3. Compare the stored records, ignoring keys, external IDs and timestamps.

A difference means a default, an audit entry or a limit exists on one path only.

## Splitting a large controller

1. Write characterization tests for the routes it serves, if they are missing.
2. Move inline validation into FormRequests first. It changes the least behaviour.
3. Move write logic into services, one use case at a time, keeping behaviour identical.
4. Split the controller by resource, or into invokable controllers per use case. Keep route names and URLs.
   Compare `php artisan route:list --json` before and after.
5. Lower the size baseline in the same change.

## Splitting a service provider

One provider per concern (container bindings, rate limiters, event wiring, observers) or per domain. Each
provider is short enough to read in one screen. Rate limiter names and event mappings stay where a reader of
that domain looks for them.

## Size ratchet

- `size-baseline.json` maps each controller and service provider to its current line count.
- CI fails when a file grows past its baseline, or when a new file exceeds the soft cap (for example 300 lines
  for controllers, 150 for providers; the project sets the numbers).
- A file that shrinks gets its baseline lowered in the same change. The baseline never rises without an ADR.
