# laravel

Architecture and production runtime rules for Laravel applications that run long-lived: domain structure, one
write path for UI and API, external IDs wired through route binding and resources, and the gaps between a green
test suite and production (Octane and queue workers holding state, SQLite versus PostgreSQL, PHP minor versions,
Valkey or Redis tiers, mail and time zone traps).

## Skills

| Skill | Use it when |
|---|---|
| `laravel-architecture` | creating or reviewing a domain, controller, service, action, DTO, enum, FormRequest or API resource |
| `laravel-production-runtime` | editing Octane, queue, cache, database, session or test configuration, adding singletons or jobs, or when tests pass locally but fail in CI or production; `octane_scan.py` finds request and tenant state in long-lived workers |

Both skills load automatically when Claude Code works with matching files (`composer.json`, `artisan`, PHP
sources, config). You can also call one directly, for example `/laravel:laravel-production-runtime`.

The skills hand stack-neutral rules to skills in the `saas` plugin (`tenant-isolation`, `dual-key-identifiers`,
`build-vs-buy`). `saas` is not a dependency of this plugin; install it for those rules.

## Install

Install this plugin at project scope, in Laravel projects only:

```bash
claude plugin marketplace add Rene-Roscher/skills
claude plugin install laravel@rene-roscher-skills --scope project
```

The plugin depends on `core` from this marketplace and on `laravel-boost` from the official marketplace
(`claude-plugins-official`). Both are installed with it. The Laravel Boost plugin adds an MCP server that runs
`php artisan boost:mcp` in the project. That command exists only when the project has the `laravel/boost`
package, so a user-scope install would start a server that fails in every non-Laravel project. In a Laravel
project without Boost, the skills suggest adding it and wait for your approval:

```bash
composer require laravel/boost --dev
php artisan boost:install
```

Source for both commands: https://laravel.com/docs/12.x/boost (verified 2026-10-31).

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off). Choices such as Horizon versus plain queue workers live in the example profile under
`templates/project-overlay/profiles/` at the repository root.

See [CHANGELOG.md](CHANGELOG.md) for changes.
