# Example profile: Laravel B2B SaaS

A profile records the choices a project made where the skills leave room. They are opinions: each is a
reasonable pick, and another project can pick otherwise without an ADR. Rules that must hold everywhere live in
the skills as `[invariant]` or `[default]`, and a profile never overrides them.

Copy this file into your project (for example `docs/profile.md`), replace what doesn't fit, and link it from
`docs/PROJECT-FACTS.md`.

## Defaults kept as written

These are `[default]` rules in the skills, listed so nobody reopens them per feature:

- External IDs: NanoID, 21 characters, alphabet `0-9a-zA-Z`, minted from a CSPRNG (`saas:dual-key-identifiers`).
- Public site as its own deployment and failure domain (`web:web-architecture`).
- Dashboards behind login as client-rendered pages, SSR off (`web:web-architecture`).
- Typed routes generated from the backend instead of string URLs (`web:web-architecture`).

## Stack

- Laravel with Inertia and Vue 3 for the product, Nuxt for the public site.
- Tailwind CSS and shadcn-vue for components, Laravel Wayfinder for typed routes.
- Laravel Fortify for headless authentication.
- PostgreSQL for transactional data, Valkey through the PhpRedis extension for cache, queues and sessions.
- Sessions in Valkey with a device list through `rene-roscher/user-sessions-laravel`.
- External API responses cached only after validation through `rene-roscher/conditional-cache-laravel`.
- Go for high-throughput workers. Payloads between services encrypted with one key per service relationship
  through the `laravel-{go,node,rust}-encryption` packages.

## Product and billing

- B2B only, prices shown net.
- A payment provider in self-managed mode behind the app's own billing interface, no billing framework.
- The tenant is called "organization" and is selected by a URL segment.
- Custom per-organization RBAC with feature-level permissions named `domain.action`.

## Backend structure

- Domains under `app/Domains/{Domain}/` with Controllers, Services, Actions, DTOs, Models and Enums.
- One public `execute()` method per service use case. DTOs are plain `final readonly` classes.
- Plain `queue:work` processes in production, one per queue. Horizon as a local dashboard only.

## Delivery

- Kubernetes, a reverse proxy with on-demand TLS for customer domains, images pinned by digest.
- Dependabot for updates, weekly, grouped per ecosystem. Renovate is equally valid.

## Working style

- Trunk-based commits to main while one person works on the repository; pull requests once a team does.
- Conventional Commits, no co-author trailers, no attribution footers.
- Reports state what was verified and what was not, with evidence linked.
- Severity P0 to P3. P0: data loss, a security breach, or the product down for all customers.
