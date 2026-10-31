# Example profile: Laravel B2B SaaS

This profile collects the project choices behind one Laravel B2B SaaS stack. They are opinions: each one is a
reasonable pick, and a different project can pick otherwise without an ADR. Rules that must hold everywhere
live in the skills as `[invariant]` or `[default]`, and this profile never overrides them.

Copy the file into your project (for example `docs/profile.md`), delete what doesn't fit, and link it from
`docs/PROJECT-FACTS.md`.

## Defaults this profile keeps as written

These are `[default]` rules in the skills, listed so nobody reopens them per feature:

- External IDs: NanoID, 21 characters, alphabet `0-9a-zA-Z`, minted from a CSPRNG (`saas:dual-key-identifiers`).
- Public site as its own Nuxt deployment and failure domain (`web:web-architecture`).
- Dashboards behind login as client-rendered Inertia pages, SSR off (`web:web-architecture`).
- Typed routes generated from the backend instead of string URLs (`web:web-architecture`).

## Product and billing

- B2B only. Registration asks for a server-side business confirmation, and the UI shows net prices with "plus
  VAT".
- Mollie as payment provider in self-managed mode: subscriptions, mandates and dunning in the app, no Laravel
  Cashier. Credit card and PayPal only.
- Annual price is 10 times the monthly price. In annual mode the per-month figure is shown as an approximation;
  the annual total is exact.
- Invoices come from an external accounting system over its API, behind an `InvoiceGenerator` interface.
- If the EU VAT number service is unreachable at checkout, charge domestic VAT and correct it once the number
  is confirmed. Review this with your tax advisor; it is a cautious choice, not a legal requirement.
- Fixed-amount coupons in whole currency units only, so the charge and the invoice agree under every rounding
  model.
- A complimentary period on a paid plan instead of a separate trial status.
- A monthly usage allowance (for example SMS credits) resets each billing cycle. Purchased packs persist.
- Dunning on day 0, 1, 3 and 7 after a failed payment, then two days of grace before the downgrade.

## Identity, tenancy and permissions

- Laravel Fortify as headless authentication; the UI is the app's own.
- The tenant is called "organization" and is chosen by a URL segment (`/orgs/{org}/...`), not by session
  state or subdomain.
- Tenant scoping is explicit on relations, backed by structural guard tests. No global tenant scope.
  PostgreSQL row-level security is an optional second line of defence, never the only one.
- Column `public_id` holds the external ID; the JSON field `id` carries it. The internal key is a PostgreSQL
  `bigserial`. One helper mints IDs and one class defines length, alphabet and validation pattern.
- Realtime channels are named `{kind}.{publicId}`.
- Cache tags `org:{id}`, `org:{id}:{area}` and `user:{id}`.
- Custom per-organization RBAC: roles store a JSONB array of about 30 feature-level permissions, no join table
  and no global roles package. Permission names follow `domain.action`, for example `invoices.edit`, grouped for
  the role editor. Teams are organisational groups and grant nothing.
- The permission cache has a five-minute TTL on top of explicit invalidation.

## Laravel backend

- Domains under `app/Domains/{Domain}/` with Controllers, Services, Actions, DTOs, Models and Enums.
- One public `execute()` method per service use case.
- DTOs are plain `final readonly` classes, no DTO package.
- Factory states are named after domain lifecycle states. Tenant fixtures go through the real
  organization-creation action, not raw factories.
- Octane on FrankenPHP for HTTP.
- Queues: plain `queue:work` processes in production, one per queue. Horizon only as a local development
  dashboard.
- Urgency-tiered queues (critical, notifications, default, bulk), plus one dedicated queue for time-critical
  notifications to people. A FIFO queue lets bulk work delay anything behind it, so that queue carries nothing
  else.
- Valkey through the PhpRedis extension, one instance per durability tier: volatile cache, durable queues,
  sessions and locks, and hot-path state.
- PHP extensions are built from the project's GitHub release tags with a SHA-256 check instead of PECL.
- The audit log is written asynchronously on its own low-priority queue and database connection, with a
  dead-letter table and a replay command.
- PgBouncer in transaction mode, with PgBouncer's prepared-statement support instead of PDO emulation
  (https://www.pgbouncer.org/config.html, `max_prepared_statements`).
- A fast SQLite test lane is kept next to the PostgreSQL lane. The PostgreSQL lane is the one that counts.

## Front end

- Nuxt for the public site, Tailwind CSS 4, shadcn-vue on Reka UI for components.
- Laravel Wayfinder for typed routes and actions.
- Inertia v2 dashboards poll with partial reloads (`usePoll` with `only`) instead of a client data library.
  Server state lives in module-singleton composables. TanStack Query or Pinia only if the lockfile already has
  them.
- URL locale prefixes with German as default and English as fallback. German copy uses the informal "du".
- Each Nuxt app has one pure cache-decision function. Security headers come from a Nitro plugin, not a module.

## Browser verification

- The Pest 4 browser plugin for the Laravel app, so browser tests share factories with feature tests. Plain
  Playwright Test for the Nuxt site.
- Dashboard viewports 1024, 1280 and 1536 pixels wide at about 700 pixels tall.
- Screenshots under `tests/Browser/Screenshots/`.
- German as the pinned locale for wording checks.

## Services and data

- Laravel is the control plane. Go for high-concurrency workers. Node only for the public site and browser
  automation.
- A Kafka-compatible log (Redpanda, with the franz-go client) between workers and the app. ClickHouse for time
  series.
- Payloads between services are encrypted with AES-256-CBC to match the app cipher, one named key per
  relationship (`[SERVICE]_ENCRYPTION_KEY`), generated by an artisan command and kept in the secret manager.
- When the metrics store is down, read endpoints return 200 with empty data, documented in the API reference.
  This is a client-compatibility choice.
- Two API-based mail providers in failover, with separate chains for alerts and transactional mail.
- EU-hosted providers where one fits. Each new third-party service gets a dependency-register entry (purpose,
  data, region, exit plan) before it ships.

## Privacy

- "Servers in Germany only" is a product promise, which makes it a test (see `saas:gdpr-engineering`).
- Avatars are initials. No third-party avatar service.
- Display names on user-generated content default to the company name.
- Messaging and push channels are opt-in per user and need a verified contact method.
- The only recurring non-transactional mail is a monthly report. Promotional mail goes only to paying customers.
- The error tracker is self-hosted in the EU.

## Infrastructure and delivery

- Hetzner Cloud, Kubernetes with RKE2, Caddy at the edge with on-demand TLS for customers' custom domains
  (https://caddyserver.com/docs/automatic-https#on-demand-tls).
- Distroless images pinned by digest. UID 65532 as the non-root user, always numeric. amd64 only until an arm64
  node exists.
- Image tags: semver for releases, `sha-` tags for pushes to main.
- Pin `NODE_OPTIONS=--max-old-space-size=...` in front-end builds; a build that passes on a workstation can run
  out of memory on a smaller CI runner.
- Dependabot rather than Renovate: weekly on Monday morning, one group per ecosystem, at most five open pull
  requests. Renovate is equally valid.
- `runs-on: ${{ vars.CI_RUNNER || 'ubuntu-latest' }}` as a per-repository escape hatch when hosted runners are
  unavailable, only together with the self-hosted runner rules in `delivery:github-actions-hardening`.
- Service containers in CI get random host ports. Long suites run as a sharded matrix with `fail-fast: false`.
- A weekly registry cleanup job. Release notes start with the command that verifies the release.

## Working style

- Trunk-based commits straight to main during the launch phase. Pull requests from feature branches once a team
  works on the repository.
- Conventional Commits, no co-author trailers, no attribution footers.
- Short reports: what was verified, what was not, with evidence linked. No narrative of the steps taken.
- Context7 as the first documentation source. No crawler installed.
- Internal documents may label evidence in German ("geprüft", "berichtet").
- Severity P0 to P3. P0: data loss, a security breach, or the product down for all customers. P1: a core
  workflow broken for many customers. P2: a workaround exists. P3: cosmetic. A P0 reaches the owner by phone at
  once.
- Investigation notes live in the issue body. The tracker moves an item to Review with a needs-verification
  label; only the owner sets Done.
- Race, idempotency, billing and authorization bugs, and adversarial plan reviews, get the strongest reasoning
  tier available.
