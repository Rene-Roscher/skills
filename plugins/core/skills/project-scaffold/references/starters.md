# Favorite starters

Use a row only for a component the approved docs name. Versions below are the ones seen on the date; look up the
current ones before you run anything (`SKILL.md`, step 3). An owner profile, `AGENTS.md` or an ADR with other
favorites wins over this file.

| Component kind | Favorite | Fallback when the approved stack differs |
|---|---|---|
| Web app with server logic, PHP | Laravel Vue starter kit (Inertia, Vue 3, TypeScript, Tailwind, shadcn-vue, Fortify) | The kit the approved stack names: `--react`, `--svelte`, `--livewire` |
| Public website, content, marketing | Nuxt, `minimal` template | The framework the approved stack names, from its own `create` command |
| Service, worker or daemon in Go | `go mod init` plus the layout from `go-service-baseline` | none |
| Anything else | The framework's official starter from its docs, flags from its `--help` | If there is no official starter, its minimal official init command |

## Laravel Vue starter kit

Seen 2026-11-04: Laravel installer 5.32.0 (Packagist), Laravel 13.17, Inertia 3, Fortify 1.37, Wayfinder, Pest 4,
Larastan, Pint. The installer prompts for every choice it is not given as a flag.

```bash
composer global show laravel/installer | grep versions   # compare with the latest on packagist.org
laravel new [directory] --vue --pest --database=pgsql --pnpm --no-boost --no-interaction
```

- `--database` follows the approved production engine (`pgsql` for PostgreSQL). The starter's own tests still run
  on SQLite in memory (`phpunit.xml`); a test lane on the production engine is a separate commit
  (`laravel-production-runtime`, `test-strategy`).
- Authentication stays on the built-in Fortify variant. `--workos` moves sign-in to WorkOS, a US identity
  provider and one more processor in the privacy docs; use it only when an ADR chose it.
- `--teams` only when the approved tenancy spec chose the kit's team model (personal team on registration, team
  slug in the URL). Otherwise tenancy follows `tenancy-model`.
- `--no-boost`: Laravel Boost is set up by `stack-bootstrap` at project scope, with one MCP definition.
- `--git` commits with the installer's own message. Leave it out and make the untouched commit yourself with
  `chore: scaffold [component] from the Laravel Vue starter kit [version]`.
- What it generates, and what stays: Fortify login, registration, password reset, email verification, two-factor
  auth, passkeys, settings pages, sidebar and header layouts, Wayfinder typed routes, about 40 Pest tests. The
  build runs through `vp` (Vite+) from `package.json`; the combined check is `composer run ci:check`.
- Defaults to align afterwards, each in its own commit: `config.platform.php` in `composer.json` set to the
  production PHP version; `QUEUE_CONNECTION`, `CACHE_STORE` and `SESSION_DRIVER` (all `database` by default)
  to what the runtime spec chose; `APP_LOCALE` to the product's default language.
- Removing a Fortify feature means removing its frontend route references too, or the Wayfinder build fails.
- Usual leftovers for the audit (from the `laravel/laravel` skeleton for framework 13.17, read 2026-11-05):
  migrations create `users`, `password_reset_tokens` and `sessions`; `cache` and `cache_locks`; `jobs`,
  `job_batches` and `failed_jobs`. `.env.example` sets `SESSION_DRIVER`, `QUEUE_CONNECTION` and `CACHE_STORE` to
  `database` and `MAIL_MAILER` to `log`, and `DatabaseSeeder` creates a demo user. When the runtime spec chose
  Redis, the `cache*` tables, `jobs` and the `sessions` table are leftovers; `failed_jobs` stays as long as
  `queue.failed.driver` is `database-uuids` (the default), and `job_batches` stays if the app uses job batches.
  `password_reset_tokens` belongs to Fortify's password reset.
- Guard test for the allowed tables, after the agreed removals: list the tables of the migrated test database
  (`Schema::getTableListing(schemaQualified: false)`; with the default `true` PostgreSQL names come back as
  `public.users`) and compare with an explicit array in the test.

## Nuxt

Seen 2026-11-04: create-nuxt 4.0.3, Nuxt 4.6. Requires Node 22 or newer (an even-numbered release).

```bash
pnpm create nuxt@latest [directory] --template minimal --packageManager pnpm --no-gitInit < /dev/null
```

- `< /dev/null` keeps it from waiting for a prompt; with these flags it asks nothing.
- `-M [modules]` installs Nuxt modules at creation. Add only modules the approved specs name (for example i18n
  when the site has more than one language).
- Then `pnpm install`, `pnpm build` and the untouched commit.

## Go

Seen 2026-11-04: Go 1.27.3.

```bash
go mod init [module path]
```

- The module path is the import path the repository will have, for example `github.com/[org]/[repo]`, not a
  placeholder.
- The `go` line in `go.mod` pins the language version; the layout (`cmd/[name]`, `internal/`), config, shutdown,
  linters and CI gates come from `go-service-baseline`.
- There is no generated test suite; the first check is `go build ./... && go vet ./...`.

## Into an existing repository

After `project-inception` the repository already holds `docs/`, `AGENTS.md` and a README. Installers want an empty
directory.

- Component in a subdirectory (`app/`, `site/`): run the installer there; nothing collides.
- Single component at the root: generate into a scratch directory outside the repository, then copy in without
  overwriting (`cp -rn [scratch]/. .`) and list every file that was skipped because it existed (usually
  `README.md`). Never use the installer's `--force` on the repository root.

## Sources

- https://laravel.com/docs/starter-kits and https://github.com/laravel/installer (`src/NewCommand.php`, options and
  `createRepository`), verified 2026-11-04; kit contents from a run of `laravel new demo --vue --pest
  --database=pgsql --pnpm --no-boost -n` with installer 5.32.0, 40 tests passed.
- `laravel/laravel` skeleton archive for framework `^13.17` (commit `06d016a`): migrations, `.env.example`, <!-- lint-allow: L13 skeleton commit the facts were read from -->
  `config/queue.php` (`failed.driver` default `database-uuids`, `batching.table`), `DatabaseSeeder`, read
  2026-11-05; `Illuminate\Database\Schema\Builder::getTableListing` in framework 13.40.0, read 2026-11-05.
- https://nuxt.com/docs/4.x/getting-started/installation and `create-nuxt --help` (4.0.3), run 2026-11-04.
- `go version` (1.27.3) and https://go.dev/ref/mod (`go mod init`), 2026-11-04.
