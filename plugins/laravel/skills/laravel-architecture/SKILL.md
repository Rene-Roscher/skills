---
name: laravel-architecture
description: "Structures Laravel SaaS code and enforces its boundaries with tests: public IDs apart from the bigint key, FormRequests, thin controllers, one write path for UI and API, one service per use case, dashboard widgets deferred and cached per tenant, Pest arch tests. Use when creating or reviewing a Laravel model, migration, controller, service, policy or API resource, or asked where code belongs. Not for Octane or queues (laravel-production-runtime)."
license: Apache-2.0
compatibility: "Laravel 11 or later on PHP 8.2 or later. Version-bound facts were checked against Laravel 12.53.0 and Pest 4.3.2."
metadata:
  author: "Rene Roscher"
paths:
  - "**/app/**/*.php"
  - "**/routes/*.php"
  - "**/tests/Arch/**"
  - "**/database/migrations/*.php"
  - "**/composer.json"
---

# Laravel architecture

This skill decides where code goes in a Laravel B2B SaaS, how the internal and the external ID of a record are
wired into the framework, and which tests make those boundaries fail the build. Framework syntax comes from the
Laravel and Pest documentation, or from the Laravel Boost MCP server's documentation search when it is installed.
The failure it prevents: a rule that lives only in a convention document while the code drifts away from it.

Precedence: an established, consistent local convention beats a `[default]` here. Say which convention you
followed. An `[invariant]` beats any local convention. Follow the invariant and report the conflict instead of
matching the codebase.

## Applies when / does not apply

- Applies: creating or reviewing a domain, model, migration, controller, service, action, DTO, enum,
  FormRequest, policy, API resource or Inertia props; a dashboard or KPI page with several sources; deciding
  where code belongs; splitting a large controller or service provider; exposing IDs; writing arch tests or
  structural guard tests.
- Does not apply: framework syntax lookups (vendor docs), Octane, queue, cache or test-environment behaviour
  (`laravel-production-runtime`), who may see which tenant's records (`tenant-isolation`; this skill only wires
  the scoped lookup), frontend code, and non-Laravel stacks (`dual-key-identifiers` holds the stack-neutral rule).

## Rules

Ordered by blast radius. The example column name `public_id` stands for whatever the project calls its external
ID column.

### Identifiers and egress

- [invariant] Internal sequential IDs never leave the server. Every externally visible model has an internal
  `bigint` key for joins and foreign keys, and a separate external ID column with a unique index for URLs, API
  payloads, page props, exports, webhooks, mails and broadcasts. Internal pivot tables get no external ID.
  Why: consecutive values let anyone enumerate records and read business volume, and 64-bit integers pass
  JavaScript's safe range of 2^53 − 1. Test: plant `'project_id' => 42` in a resource; the leak guard fails.
  Source: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER (verified 2026-10).
- [invariant] External IDs come from a CSPRNG: `random_bytes()` with rejection sampling, or a library mode
  built on it. Read the ID library's source at the locked version before trusting its default.
  `hidehalo/nanoid-php` 2.0 `generateId()` defaults to a mode built on `mt_rand()`; its dynamic mode and
  `formattedId()` use `random_bytes()`. Why: a non-cryptographic PRNG's state can be recovered, which makes
  later IDs predictable. Test: a unit test calls `mt_srand(42)` before each of two `generate()` calls and
  asserts the IDs differ (an `mt_rand`-based generator returns the same ID twice; reproduced against
  hidehalo/nanoid-php 2.0 on 2026-10-31); `arch()->preset()->security()` passes (in Pest 4.3.2 it forbids
  `rand`, `mt_rand` and `uniqid` in app code); 10,000 minted IDs have the right length and alphabet and no
  duplicates. Source: hidehalo/nanoid-php 2.0 `src/Client.php`, Pest 4.3.2 `src/ArchPresets/Security.php`
  (read 2026-10).
- [invariant] Records are resolved and rendered by external ID only. Implicit route binding uses the external
  column. API resources and Inertia props map `'id' => $this->public_id` and expose relations by the related
  model's external ID, never as `*_id` integers. Route binding resolves an ID; it does not authorize.
  Tenant-owned records are fetched through the tenant relation or scoped bindings, so a foreign ID and a
  missing ID both return 404. Why: global binding alone resolves another tenant's record by its valid ID.
  Test: a request for another tenant's ID returns the same 404 as an unknown ID. Source:
  https://laravel.com/docs/13.x/routing (scoped implicit binding, via Context7, verified 2026-10).
- [default] One model trait owns the external ID: its `creating` hook fills the column when empty, and
  `getRouteKeyName()` returns that column. Trade-off: every externally visible model needs the trait, and
  models that bind by another key need an override. Deviate only with an ADR that names this trade-off.
  Why: a second, hand-rolled ID path drifts. Proof: a reflection test asserts that every model in the domain
  model namespaces uses the trait (allowlist with reasons).
- [invariant] A global ID-leak guard inspects every feature-test response: JSON bodies, Inertia page props,
  `Location` headers and base64 pagination cursors. It fails on an integer or digit-only string under `id`,
  `*_id` or `*_ids`. Allowlist entries carry a written reason (staff panel, machine-to-machine endpoint, a
  foreign system's key such as a chat platform's `chat_id`). `report` and `off` modes exist for migrating
  legacy code and are never set in CI. Why: a review rule covers the endpoints someone thought of; a response
  guard turns the existing suite into a sweep. Test: the guard's self-test feeds it a leaking body, prop,
  cursor and redirect and expects four failures; `${CLAUDE_SKILL_DIR}/scripts/id-leak-check.py payload`
  reproduces the check on a captured response.
- [invariant] Every egress channel that HTTP tests don't see gets its own leak test: broadcasts, rendered
  mails, outbound webhook bodies, CSV and JSON exports, queued notification payloads. Never cursor-paginate on
  the internal `id`, because the cursor is base64-encoded JSON of the sort columns. Order by a timestamp plus
  the external ID as tie-breaker. Why: these are the blind spots of a response-only guard. Test: one test per
  channel the project has runs the shared checker on the captured payload; a cursor from each index endpoint
  decodes to no integer ID. Source: laravel/framework v12.53.0
  `src/Illuminate/Pagination/Cursor.php` `encode()` (read 2026-10).
- [invariant] Privilege flags and tenant pointers (`is_admin`, `current_tenant_id`) are never
  mass-assignable. Keep them out of `$fillable` and set them with `forceFill()` in privileged code only.
  Why: one self-service form that passes `validated()` into `fill()` becomes a privilege escalation.
  Test: `fill()` and `create()` with each such key leave the attribute unchanged, one test per attribute.
- [invariant] Every external ID in input is validated against the current tenant:
  `Rule::exists(table, 'public_id')->where(tenant column, current tenant)`, and an array of IDs as one set by a
  rule object. Why: an unscoped `exists` lets a request attach another tenant's record. Test: a request that
  references another tenant's ID fails exactly like one with an unknown ID. `tenant-isolation` owns the
  general rule.
- [default] The external ID is a NanoID: 21 characters from the 62-character alphabet `0-9a-zA-Z` (no `-`
  or `_`), about 125 bits (21 × log2 62). Trade-off: random IDs insert at scattered positions in the unique
  index on the external column (page splits, worse cache locality); time-ordered formats such as UUIDv7 and
  ULID insert in order but reveal the creation time to anyone holding the ID. Deviate only with an ADR that
  names this trade-off. Source: https://www.rfc-editor.org/rfc/rfc9562.html sections 2.1, 5.7 and 6.11,
  https://github.com/ulid/spec (verified 2026-10).
- [default] On surfaces that people or agents read (support tools, CLI output, tool-calling interfaces,
  logs), external IDs carry a kind prefix such as `inv_` and are resolved only inside tenant-scoped queries.
  Trade-off: longer strings and a prefix registry to keep. Deviate only with an ADR that names this
  trade-off. Proof: a wrong-kind handle gets a 4xx that names the expected kind; another tenant's handle
  gets the same 404 as an unknown one (`dual-key-identifiers`).

### Layering

- [invariant] Code is the ground truth for architecture claims. Before applying a project's architecture
  document or one of its examples, check the named classes, folders and packages in the code and the
  lockfile. Report drift with `path:line` instead of bringing back what the code removed, and never copy a
  documented example that breaks an invariant, such as props that ship an internal `id`. Why: architecture
  docs drift within weeks, and an agent that trusts them reintroduces removed packages and leaky examples.
  Test: the report lists each checked claim with `path:line` or "not found" (`evidence-before-claims`).
- [default] Validation lives in FormRequests. No `$request->validate()`, `Validator::make()` or
  `$this->validate()` in controllers; every write has a FormRequest with `authorize()` and `rules()`. Bounds
  come from shared constants that mirror the database CHECK constraints. Trade-off: one more class per write
  endpoint. Deviate only with an ADR that names this trade-off. Proof: a token-scanning test over controller
  directories fails on those calls; allowlist entries need a reason.
- [default] Controllers stay thin, and UI and API share one write path: request, FormRequest, service or
  action, then resource or response. API controllers never call `::create`, `->save()`, `->update()` or
  `->delete()`; they call the same domain service as the UI controller. Trade-off: a service class even for
  simple CRUD. Deviate only with an ADR that names this trade-off. Proof: a scanner test for model writes in
  API controllers, and a parity test per resource that web and API store the same state for the same input.
- [default] A page with several widgets computes nothing in its controller: each widget is one query class
  that returns a DTO; the controller maps it to a load mode (cheap in the first response, expensive as
  `Inertia::defer` in its own group with `rescue: true`, below the fold as `Inertia::optional`); every widget
  reads through one cache helper keyed by tenant, widget and the viewer's visibility, with `Cache::flexible`
  fresh and stale times from the widget's freshness need and a lock on the cold path; KPIs that aggregate more
  rows than the request budget allows read a rollup table that a scheduled job fills. Trade-off: one class, one
  cache entry and possibly one rollup per widget. Deviate only with an ADR that names this trade-off. Proof: the
  group test (`missing`, `loadDeferredProps` per group) and a cold and warm query count per widget, warm with
  zero queries, in references/dashboard-data.md. Source: https://laravel.com/docs/13.x/cache ("Stale While
  Revalidate", "Atomic Locks"); `Illuminate\Cache\Repository::flexible` locks only the background refresh
  (13.x source); https://inertiajs.com/docs/v3/data-props/deferred-props; all verified 2026-11-06.
- [default] A size ratchet holds large classes: a committed baseline of line counts per controller and
  service provider, which a file may shrink below but never grow past, and a soft cap for new files. A
  provider that mixes bindings, rate limiters and event wiring is split by concern or domain. Trade-off: the
  baseline file needs updating when a class shrinks. Deviate only with an ADR that names this trade-off.
  Proof: the CI step in [references/guard-artifacts.md](references/guard-artifacts.md).
- [default] Code lives in domain folders such as `app/Domains/{Domain}/{Controllers,FormRequests,Services,Actions,DTOs,Enums,Models,Policies,Jobs,Events,Listeners,Resources}`,
  with only the folders a domain needs, and the model sits in its owning domain. Domains that must not leak
  are fenced with `toOnlyBeUsedIn`. An existing app with a different, consistent layout keeps it. Trade-off:
  deeper namespaces than the stock skeleton, and the Pest Laravel preset no longer fits. Deviate only with an
  ADR that names this trade-off. Proof: per-layer arch rules in
  [references/arch-tests.md](references/arch-tests.md).
- [default] A service class is one use case with exactly one public entry method; pick one name for the
  whole project (`execute` or `handle`) and enforce it. Actions are single-purpose steps reused by several
  services. Read-only classes may have several public methods and are named `...Query` or `...Reader`.
  Trade-off: more, smaller classes. Deviate only with an ADR that names this trade-off. Proof: a reflection
  test over `App\Domains\*\Services` asserts one public non-magic method with the chosen name.
- [default] Data that crosses a layer boundary is a `final readonly` class. Every closed value set is a
  string-backed enum, mirrored by a database CHECK constraint and validated with `Rule::enum()`. Trade-off:
  a DTO class per boundary and a migration per new enum case. Deviate only with an ADR that names this
  trade-off. Proof: `toBeFinal()->toBeReadonly()` on the DTO namespaces, `toBeEnums()` on the enum
  namespaces, and a PostgreSQL-lane test that an unknown status violates the constraint.
  Source: Pest 4.3.2 `src/Expectation.php` (read 2026-10).
- [default] Replaceable vendors (payments, mail, SMS, storage) sit behind an interface the domain owns, with
  one adapter per vendor and a test adapter. The vendor SDK is used only inside its adapter. Permissions,
  tenancy, billing rules and audit are built in-house (`build-vs-buy`). Trade-off: an adapter layer to keep,
  and vendor features that need the interface widened. Deviate only with an ADR that names this trade-off.
  Proof: `toOnlyBeUsedIn` on each SDK namespace, and a container test that the interface resolves to the
  configured adapter.

### Enforcement

- [default] Every PHP file declares `strict_types=1`, and `dd`, `dump`, `ray` and `var_dump` never appear in
  `app/`. Trade-off: conversions at boundaries must be written out. Deviate only with an ADR that names this
  trade-off. Proof: `arch()->expect('App')->toUseStrictTypes()->not->toUse(['dd', 'dump', 'ray', 'var_dump'])`
  and `arch()->preset()->php()`. List `dd` yourself: the php preset in Pest 4.3.2 forbids `dump`, `ray` and
  `var_dump` but not `dd`. Source: https://pestphp.com/docs/arch-testing (via Context7), Pest 4.3.2
  `src/ArchPresets/Php.php` (verified 2026-10).
- [default] Every "remember to X" becomes a structural test. When a rule cannot be an arch expectation (a raw
  `DB::table()` on a tenant table, a `cursor()` call whose eager loads are silently dropped, a metered record
  created outside its budget service), a token-scanning test over `app/` fails on the construct, with an
  allowlist that needs a reason per entry. Plant a violation once and watch each new guard fail. Trade-off: guard upkeep and
  allowlist reviews. Deviate only with an ADR that names this trade-off. Proof: the guard and its recorded
  red run ([references/structural-guards.md](references/structural-guards.md)).
- [default] PHPStan with Larastan runs at a fixed level with a committed baseline that only shrinks. Pick the
  Larastan major that its README's supported-versions table lists for the installed Laravel version.
  Trade-off: baseline upkeep, and some dynamic code needs annotations. Deviate only with an ADR that names
  this trade-off. Why: a missing `use` import otherwise surfaces only at runtime in a path no test runs.
  Source: https://phpstan.org/user-guide/baseline, https://github.com/larastan/larastan (verified 2026-10).

## Procedure

1. Read `composer.json` and `composer.lock`: PHP, Laravel, Pest, Larastan and ID library versions. If
   `laravel/boost` is missing from `require-dev`, propose `composer require laravel/boost --dev` and
   `php artisan boost:install`, and wait for approval.
2. Read the project's facts file and architecture notes. Check every claim you rely on against code and
   lockfile, and note drift with `path:line`.
3. Record the local conventions: folder layout, service entry method, external ID column and format,
   FormRequest location. A consistent convention wins over a `[default]`; an `[invariant]` wins over a
   convention.
4. Place the code ([references/layering.md](references/layering.md)). For a new externally visible model:
   migration with the external column and unique index, the trait, resource and props mapping, scoped lookup
   ([references/dual-key-ids.md](references/dual-key-ids.md)).
5. Write the feature test that calls the new endpoint, so the leak guard runs over it. Add an egress test for
   any new channel ([references/id-leak-guard.md](references/id-leak-guard.md)).
6. Before using an arch expectation, preset or framework method you have not seen in this project, search
   `vendor/` for it or query the docs for the installed version. If neither shows it, say it is unverified and
   use a confirmed alternative.
7. Add or extend arch and structural guards. Plant a violation once and see each new guard fail.
8. Run the suite, the arch tests and static analysis. Report what ran and what you could not run.

## Traps

- The Pest Laravel preset fails a domain layout. In Pest 4.3.2, `arch()->preset()->laravel()` expects enums
  only in `App\Enums`, models only in `App\Models` and FormRequests only in `App\Http\Requests`
  (`src/ArchPresets/Laravel.php` lines 26, 64 and 78). Write the domain-aware rules instead.
- The strict preset is more than strict types. In Pest 4.3.2, `arch()->preset()->strict()` also requires
  every class to be final and forbids protected methods and abstract classes (`src/ArchPresets/Strict.php`).
  Use `toUseStrictTypes()` when strict types are all you want.
- Invented expectations. Pest 4.3.2 has `toBeFinal`, `toBeReadonly`, `toBeEnums`, `toHaveSuffix`,
  `toOnlyBeUsedIn`, `toUseStrictTypes` and `toHaveMethod`, and nothing DTO-specific. A plausible name such as
  a "toBeDTO" expectation does not exist; the source search in step 6 catches it.
- A cursor looks opaque but is base64 JSON. Ordering a cursor-paginated endpoint by `id` puts the internal key
  into every next-page link.
- `Model::with(...)->cursor()` drops the eager loads without a warning, and every relation becomes one query
  per row. Use `lazy()` when relations are needed (https://laravel.com/docs/13.x/eloquent, "Cursors", via
  Context7, verified 2026-10). The eager load often sits in another method, so the guard flags every
  `cursor()` that lacks an annotation saying it touches no relations.
- Route binding without scoping resolves another tenant's record by its valid external ID.
- `Cache::flexible` refreshes a stale value under a lock, but a missing value is computed by every concurrent
  request at once. A dashboard right after a deploy or a tag flush is exactly that case.
- `Cache::lock()->block()` measures its wait with `Carbon::now()`; under `freezeTime()` a held lock never times
  out and the test hangs.
- A convention document without a test drifts. Large controllers and inline validation pile up while the doc
  still says "thin controllers". Count before you claim that a codebase follows its convention.
- Documented examples leak. An example in a project doc that passes `$model->id` into props gets copied into
  new pages. Check examples against the invariants before reusing them.
- Shape validation decides nothing. When the ID alphabet is tightened later, keep the shape check accepting the
  old alphabet so old URLs still resolve. Existence and tenant come from the scoped lookup.

## Done when

- Every new or changed externally visible model uses the trait, and its resources and props map `id` to the
  external ID.
- The leak guard runs over every new endpoint and passes, and its self-test still fails on planted leaks.
- Every write has a FormRequest, and referenced IDs validate against the current tenant.
- Each new arch or structural guard was seen failing once on a planted violation.
- Static analysis passes at the fixed level, and the baseline did not grow.
- A multi-widget page has a cost row per widget (load mode, TTL, cold and warm query count) and the group test.
- Conflicts between an invariant and a local convention, and drift between docs and code, are reported with
  `path:line`.

## References

- [references/dual-key-ids.md](references/dual-key-ids.md): load when adding a model, migration, route
  binding, resource, cursor pagination, or choosing an ID format.
- [references/id-leak-guard.md](references/id-leak-guard.md): load when writing or extending the leak guard,
  adding an egress channel, or running legacy code in `report` mode.
- [references/layering.md](references/layering.md): load when placing new code, splitting a large controller
  or provider, or choosing between service, action and DTO.
- [references/arch-tests.md](references/arch-tests.md): load when writing `arch()` rules, presets,
  `ignoring()` entries or namespace wildcards.
- [references/structural-guards.md](references/structural-guards.md): load when a rule cannot be written as
  `arch()` and needs a token scanner with an allowlist.
- [references/vendor-boundaries.md](references/vendor-boundaries.md): load when integrating a payment, mail,
  SMS or storage vendor.
- [references/dashboard-data.md](references/dashboard-data.md): load when building a dashboard or any page with
  several widgets, KPIs or aggregates: query classes, widget cache, rollups, cold and warm measurement.
- [references/adr-template.md](references/adr-template.md): load when deviating from a `[default]`.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when setting up the guard tests in a
  project, or checking which ones exist.
- [scripts/id-leak-check.py](scripts/id-leak-check.py): run
  `python3 ${CLAUDE_SKILL_DIR}/scripts/id-leak-check.py --help` to check captured payloads or PHP sources for
  internal IDs.

## Sources

- https://laravel.com/docs/13.x/cache: `Cache::flexible`, atomic locks and the drivers that support them, tags,
  verified 2026-11-06; https://inertiajs.com/docs/v3/data-props/deferred-props and
  https://inertiajs.com/docs/v3/advanced/testing: groups, `rescue`, `loadDeferredProps`, verified 2026-11-06.
- https://www.rfc-editor.org/rfc/rfc9562.html: UUIDv7 carries a 48-bit Unix millisecond timestamp in its most
  significant bits (5.7); time-ordered UUIDs have better index locality and UUIDv4 poor (2.1, 6.11). Verified
  2026-10.
- https://github.com/ulid/spec: ULID starts with a 48-bit millisecond timestamp and sorts lexicographically.
  Verified 2026-10.
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER:
  JavaScript's safe integer limit 2^53 − 1. Verified 2026-10.
- https://laravel.com/docs/13.x/routing: scoped implicit binding (`{post:slug}`, `scopeBindings()`), via
  Context7. Verified 2026-10.
- https://laravel.com/docs/13.x/eloquent ("Cursors"): `cursor()` cannot eager load relationships; `lazy()` can.
  Via Context7, verified 2026-10.
- https://pestphp.com/docs/arch-testing: arch expectations, presets and wildcards. Expectation and preset
  details read in the Pest 4.3.2 source. Verified 2026-10.
- https://phpstan.org/user-guide/baseline and https://github.com/larastan/larastan: baseline workflow and the
  Larastan supported-versions table. Verified 2026-10.
- https://laravel.com/docs/12.x/boost: installing Laravel Boost. Verified 2026-10.
- hidehalo/nanoid-php 2.0 `src/Client.php` and laravel/framework v12.53.0
  `src/Illuminate/Pagination/Cursor.php`: read in the installed source, 2026-10.
