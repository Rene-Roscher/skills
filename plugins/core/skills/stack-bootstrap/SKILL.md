---
name: stack-bootstrap
description: "Detects a repository's stack from its files (composer.json, go.mod, package.json, Dockerfile, workflows, Terraform, Helm, Kustomize, Ansible) and enables the matching plugins of this marketplace plus a curated third-party set, per project. Use when setting up the agent in a new or cloned repo, or after the stack changed. Not for choosing a stack or writing app config."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Stack bootstrap

This skill decides which agent plugins and skills a repository gets, and at which scope. It reads the files that
name the stack, maps each signal to a plugin of this marketplace or to an entry of the curated third-party list,
enables them at project scope in the committed `.claude/settings.json`, and verifies that they load. How each
plugin works is in its own docs. The failure it prevents: stack tooling enabled for every repository on the machine
(a Laravel MCP server that fails to start in a Go repo), teammates who get different tools than the author, and a
setup that stays frozen while the stack moves on.

## Applies when / does not apply

- Applies: a new or freshly cloned repository without `.claude/settings.json`; "set up Claude Code", "which
  plugins should this repo use", "install Laravel Boost", "add the Postgres or Redis skills"; a stack change such as
  a new language, a new datastore, a Dockerfile, CI workflows or infrastructure code; a teammate reporting that a
  plugin is missing.
- Does not apply: choosing a framework or database, adding application dependencies, writing Dockerfiles or CI
  workflows (`container-images`, `github-actions-hardening`), authoring new skills, configuring permissions
  unrelated to plugins.

## Detection signals

Read only the files below. Each enabled plugin is backed by at least one path.

| Signal (file and content) | Enable |
|---|---|
| any repository | `core` |
| any manifest with third-party dependencies | `docs-tools` (installs Context7 from the official marketplace) |
| `composer.json` requires `laravel/framework` | `laravel`, plus `laravel-boost` from `claude-plugins-official` |
| `go.mod` | `go` |
| `package.json` depends on `vue`, `nuxt`, `@inertiajs/vue3` or `reka-ui` | `web` |
| `Dockerfile`, `Containerfile`, `compose*.yaml`, `.github/workflows/*.yml` | `delivery` |
| `*.tf`, `*.tofu`, `Chart.yaml`, `kustomization.yaml`, `ansible.cfg`, `playbooks/`, `roles/*/tasks/` | `infra` |
| PostgreSQL: `pgsql` default connection, a `postgres` image in compose, `pgx`, `lib/pq`, `pg`, `postgres` packages | `data`, plus `supabase-postgres-best-practices` |
| Redis or Valkey: a `redis` or `valkey` image, `predis/predis`, `ext-redis`, `go-redis`, `ioredis`, `redis` packages | `redis-development` from `claude-plugins-official` |
| ClickHouse: a `clickhouse` image or a ClickHouse client package | `clickhouse-best-practices` from `claude-plugins-official` |
| an MCP SDK dependency, for example `@modelcontextprotocol/sdk` or `laravel/mcp` | `api` |
| none (product type, not a file) | `saas` and `business`: offer them, the owner decides |

Monorepos: scan each top-level app directory. A plugin is enabled once for the repository when any app has the
signal; say which app produced it.

## Rules

- [invariant] Enable a plugin only on evidence: a detection signal with its path, or an explicit request from the
  owner. Report each plugin with the file that triggered it, and each skipped curated entry with the missing
  signal. Why: plugins add context and start servers in every session of the repository. Test: run on a repository
  with `go.mod` and no `composer.json`; the report enables `go` with `go.mod` as evidence and lists `laravel-boost`
  as skipped. Source: reproducible with the test above.
- [invariant] Stack plugins are enabled at project scope, never user scope; `laravel-boost` above all. Why: the
  `laravel-boost` plugin is only an MCP server definition that runs `php artisan boost:mcp`, which fails in any
  directory without an `artisan` file, so a user-scope install starts a broken server in every other repository.
  Test: `claude plugin list` in a non-Laravel repository shows no enabled `laravel-boost`; in the Laravel repository
  `.claude/settings.json` holds `"laravel-boost@claude-plugins-official": true`. Source: the plugin's `.mcp.json` in
  the `claude-plugins-official` marketplace (read 2026-11-03); install scopes in
  https://code.claude.com/docs/en/discover-plugins (verified 2026-11-03).
- [invariant] Ask before any command that changes the project's dependency manifests or writes outside `.claude/`:
  `composer require laravel/boost --dev`, `php artisan boost:install`, `npx skills add`. Show the command, the files
  it touches and what it adds; run it only after a yes. Why: these change `composer.json` and the lock file, and
  `boost:install` generates guideline, skill and MCP files such as `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and
  `boost.json`. Test: in a Laravel fixture, the agent proposes the composer command and waits; `composer.json` is
  unchanged until the answer. Source: https://laravel.com/docs/12.x/boost (verified 2026-11-03).
- [invariant] The shared setup lives in the committed `.claude/settings.json`: `extraKnownMarketplaces` declares
  this marketplace and `enabledPlugins` lists every chosen plugin. Personal additions go to
  `.claude/settings.local.json`. No API key or token appears in a committed file. Why: only the committed file
  reaches teammates; a key there leaks with the repository. Test: the file parses as JSON, and
  `git grep -nE 'API_KEY|TOKEN' -- .claude/settings.json` prints nothing. Source:
  https://code.claude.com/docs/en/settings (verified 2026-11-03).
- [invariant] Enabled is not installed. The bootstrap ends with the one-time install line for teammates in the
  project's agent docs (`claude plugin install [name]@[marketplace] --scope project` per plugin), and with a check
  in the current session: each chosen plugin is listed as enabled at project scope and its skills appear under
  `/[plugin]:`. Why: committing `enabledPlugins` turns a plugin on for collaborators but does not download it, and
  `extraKnownMarketplaces` applies only after each person trusts the folder. Test: `claude plugin list` shows every
  plugin from `enabledPlugins` with scope `project`. Source: https://code.claude.com/docs/en/discover-plugins and
  https://code.claude.com/docs/en/settings (verified 2026-11-03).
- [invariant] In a Laravel repository, exactly one Boost MCP connection exists, from one definition the team
  chose. After `boost:install`, compare its `.mcp.json` entry with the plugin's command and delete the definition
  you do not keep. Why: Claude Code treats a plugin server with the same command as a project entry as a duplicate
  and connects to the project entry, but a different command (a container wrapper, another PHP binary) makes two
  servers with the same tools. Test: `/mcp` lists one connected Boost server. Source:
  https://code.claude.com/docs/en/mcp, scope precedence and duplicate matching by endpoint (verified 2026-11-03).
- [default] Third-party skills and plugins come only from `references/curated-skills.md`, installed with the
  command listed there. Anything else is added on an explicit owner request and then recorded in that list with a
  verified date. Trade-off: a useful new skill waits until someone adds it to the list. Deviate only with an ADR
  that names this trade-off. Source: reproducible: every entry in `enabledPlugins` and every installed skill
  directory maps to a row of the list or to this marketplace.
- [default] Pin this marketplace to a release tag in `extraKnownMarketplaces` (`"ref"`), and bump the tag on
  purpose. Trade-off: fixes arrive only after a bump. Deviate only with an ADR that names this trade-off. Source:
  https://code.claude.com/docs/en/discover-plugins, `#ref` pins a branch or tag (verified 2026-11-03).
- [default] Run `npx skills add` with `DISABLE_TELEMETRY=1` and an explicit `--skill` and `-a claude-code`, and
  commit the files it writes so teammates get the same version. Trade-off: the CLI's authors receive no usage
  data; a committed copy needs a manual update. Deviate only with an ADR that names this trade-off. Source:
  https://github.com/vercel-labs/skills README: "Set `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` to disable
  telemetry and security-audit requests" (verified 2026-11-03).
- [default] Re-run the bootstrap when a detection file changes: a new dependency in `composer.json`,
  `package.json` or `go.mod`, a new Dockerfile, workflow or infrastructure directory, or a removed datastore.
  Enable what is new and disable what lost its signal (`claude plugin disable [name]@[marketplace] --scope
  project`). In Laravel repositories, refresh Boost's generated files with `php artisan boost:update` after
  dependency updates. Trade-off: a stack change is a two-step review (code plus agent setup). Deviate only with an
  ADR that names this trade-off. Source: https://laravel.com/docs/12.x/boost, `boost:update` (verified
  2026-11-03); reproducible: the detection report and `enabledPlugins` list the same plugins.

## Procedure

1. Gate: is this a repository root? Read `.claude/settings.json` if it exists; this run updates it rather than
   replacing it.
2. Detect: read only the signal files in the table. Note each match with its path.
3. Propose: one table with plugin, marketplace, evidence path and scope (always `project`), then the curated
   third-party entries with their install commands, then commands that need a yes (composer, artisan, npx).
4. Write `.claude/settings.json`: merge `extraKnownMarketplaces` and `enabledPlugins` into the existing file; keep
   its other keys. Template and merge rules: `references/team-settings.md`.
5. Install for the current user: `claude plugin install [name]@[marketplace] --scope project` per plugin. In a
   script on a fresh machine, add the official marketplace first.
6. Laravel only, after a yes: `composer require laravel/boost --dev`, then `php artisan boost:install`. Commit or
   back up an existing `CLAUDE.md` and `AGENTS.md` first and review the diff afterwards. Keep one Boost MCP
   definition.
7. Curated skills after a yes: run the commands from `references/curated-skills.md`.
8. Verify: `claude plugin list`, `/mcp`, and one skill per plugin visible under `/[plugin]:`. In a running session,
   run `/reload-plugins` first.
9. Write the teammate install lines into the project's agent docs and report what was enabled, skipped and left
   for a decision.

## Traps

- A user-scope install of a stack plugin looks fine in the repository where it was installed and starts failing
  servers everywhere else.
- `boost:install` regenerates agent guideline files. Run it in a clean working tree so the diff shows exactly what
  it changed in a hand-written `CLAUDE.md` or `AGENTS.md`.
- The official marketplace is added on the first interactive session; a setup script on a fresh machine has to
  add it explicitly or the install fails.
- A committed `enabledPlugins` entry without the install line in the docs leaves teammates with a warning that the
  plugin is enabled but not installed.
- Detecting PostgreSQL from `.env` reads a secret-bearing file. Use `.env.example`, config defaults and compose
  files instead.
- A monorepo scanned only at the root misses the frontend in `apps/web/package.json`.

## Done when

- Every enabled plugin has an evidence path or an owner request in the report.
- `.claude/settings.json` parses, declares this marketplace pinned to a tag, lists the chosen plugins and holds no
  secrets.
- `claude plugin list` shows each chosen plugin enabled at project scope; `/mcp` shows one Boost server in
  Laravel repositories and none elsewhere.
- Commands that changed manifests ran only after a yes, and their diffs were reviewed.
- The project's agent docs carry the teammate install lines.

## References

- [references/curated-skills.md](references/curated-skills.md): load when installing or updating a third-party
  skill or plugin, or when someone asks for one that is not in the list.
- [references/team-settings.md](references/team-settings.md): load when writing or merging
  `.claude/settings.json`, onboarding a teammate, or re-running after a stack change.

## Sources

- https://code.claude.com/docs/en/discover-plugins: install scopes, `--scope project`, enabled versus installed,
  official marketplace registration, verified 2026-11-03.
- https://code.claude.com/docs/en/settings: shared and local project settings, `extraKnownMarketplaces` waiting for
  trust, verified 2026-11-03.
- https://code.claude.com/docs/en/mcp: server precedence, duplicates matched by endpoint for plugin servers,
  verified 2026-11-03.
- https://laravel.com/docs/12.x/boost: `composer require laravel/boost --dev`, `boost:install`, `boost:update`,
  `boost:mcp`, generated files, verified 2026-11-03.
- https://github.com/vercel-labs/skills: `npx skills add`, `--skill`, `-a`, project scope by default,
  `DISABLE_TELEMETRY`, verified 2026-11-03.
- https://github.com/supabase/agent-skills: `supabase-postgres-best-practices` install command, verified 2026-11-03.
