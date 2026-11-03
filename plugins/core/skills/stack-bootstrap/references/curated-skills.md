# Curated third-party skills and plugins

The set the bootstrap installs besides this marketplace's own plugins. Each row names the signal that selects it.
Names and sources were checked against the `claude-plugins-official` marketplace manifest and the upstream READMEs
on the verified date. Re-check a row when its command fails or the upstream renames it, and update the date.

| Name | What it adds | Selected by | Install (project scope) | Verified |
|---|---|---|---|---|
| `laravel-boost` (marketplace `claude-plugins-official`) | MCP server definition only: runs `php artisan boost:mcp` in the project. Tools include application info, database schema and read queries, log and last-error reading, browser logs, absolute URLs and a docs search scoped to the installed package versions | `composer.json` requires `laravel/framework` | `claude plugin install laravel-boost@claude-plugins-official --scope project` | 2026-11-03 |
| `laravel/boost` (Composer package, needed by the plugin above) | The `boost:mcp` command the plugin starts, plus generated guidelines and skills for the installed Laravel packages | same as above | After a yes: `composer require laravel/boost --dev`, then `php artisan boost:install`; later `php artisan boost:update` | 2026-11-03 |
| `context7` via this marketplace's `docs-tools` | Hosted documentation MCP server for version-specific library docs; works without a key, `CONTEXT7_API_KEY` raises rate limits | any manifest with third-party dependencies | `claude plugin install docs-tools@rene-roscher-skills --scope project` (installs `context7@claude-plugins-official` as a dependency) | 2026-11-03 |
| `redis-development` (marketplace `claude-plugins-official`, source `redis/agent-skills`) | Redis practices: data structures, query engine, vector search, caching, performance | Redis or Valkey signal | `claude plugin install redis-development@claude-plugins-official --scope project` | 2026-11-03 |
| `clickhouse-best-practices` (marketplace `claude-plugins-official`, source `ClickHouse/agent-skills`) | 28 rules for ClickHouse schema design, query optimization and ingestion, ordered by impact | ClickHouse signal | `claude plugin install clickhouse-best-practices@claude-plugins-official --scope project` | 2026-11-03 |
| `supabase-postgres-best-practices` (repository `supabase/agent-skills`) | Postgres guidance in eight categories: query performance, connection management, schema design, concurrency and locking, security and RLS, data access patterns, monitoring, advanced features | PostgreSQL signal | After a yes: `DISABLE_TELEMETRY=1 npx skills add supabase/agent-skills --skill supabase-postgres-best-practices -a claude-code` | 2026-11-03 |
| `frontend-design` (marketplace `claude-plugins-official`, same skill as `anthropics/skills`) | Anthropic's guidance for a deliberate visual direction instead of template defaults: typography, colour, motion, composition | a browser UI: the `web` signal, or `package.json` depends on `react`, `svelte` or `@angular/core` | `claude plugin install frontend-design@claude-plugins-official --scope project` | 2026-11-03 |
| `web-design-guidelines` (repository `vercel-labs/agent-skills`) | Vercel's review of UI code against its Web Interface Guidelines (accessibility, focus, forms, motion, typography, URL state), findings as `file:line` | same as above | After a yes: `DISABLE_TELEMETRY=1 npx skills add vercel-labs/agent-skills --skill web-design-guidelines -a claude-code` | 2026-11-03 |
| `kumo-design` (repository `cloudflare/kumo`) | Cloudflare's product design rules for Kumo interfaces: text size, heading case, weights, spacing, borders and shadows, radii, dialogs | `package.json` depends on `@cloudflare/kumo` | After a yes: `DISABLE_TELEMETRY=1 npx skills add cloudflare/kumo --skill kumo-design -a claude-code` | 2026-11-03 |

## Notes per entry

- `laravel-boost`: the plugin and the Composer package are two halves. Without the package, the plugin's server
  fails to start; without the plugin, `boost:install` can still register the server in `.mcp.json`. Use one of the
  two definitions, not both with different commands. Boost's docs suggest the generated `.mcp.json`, guideline
  files and `boost.json` may be gitignored because `boost:install` and `boost:update` regenerate them; decide that
  per repository and record it. To refresh after dependency updates, Boost documents a Composer
  `post-update-cmd` entry `@php artisan boost:update --ansi`.
- `context7`: keep `CONTEXT7_API_KEY` in the user's environment or in `.claude/settings.local.json`, never in the
  committed settings file.
- `supabase-postgres-best-practices`: the upstream also publishes it as a plugin (`claude plugin marketplace add
  supabase/agent-skills`, then `claude plugin install postgres-best-practices@supabase-agent-skills`). Use one of
  the two forms per repository. `npx skills add` installs into the current project by default; `-g` would make it
  global, which the bootstrap does not use. Review the written files with `git status` and commit them.
- `redis-development` and `clickhouse-best-practices` are pinned by the official marketplace to an upstream commit;
  the official marketplace updates automatically, so their content can change between sessions.
- `frontend-design`: pushes toward a distinctive new direction. In a product with existing screens, this
  marketplace's `design-quality` skill keeps the product's own artifact as the first reference; the two agree,
  because `frontend-design` also says to follow a visual direction the brief pins down.
- `web-design-guidelines`: the installed skill is a short wrapper. At each review it downloads the current
  guideline list from the upstream repository, so it needs network access and its rules can change between runs
  without a change in the committed copy. Vercel's own guidelines page names this install command.
- `kumo-design`: its rules use Kumo components in the examples. Without `@cloudflare/kumo` the skill would
  steer code toward a library the project does not use, so it is selected only by that dependency.
- `npx skills add` writes `skills-lock.json` next to `.claude/skills/`; commit both.
- On a machine where no interactive session has run yet, a script adds the official marketplace first:
  `claude plugin marketplace add anthropics/claude-plugins-official`.

## Adding an entry

Add a row only on an owner request. Fill every column, take the name and source from the marketplace manifest or
the upstream README (not from memory), run the install command once in a scratch repository, and put that day's
date in the last column.

## Sources

- https://laravel.com/docs/12.x/boost, verified 2026-11-03.
- https://github.com/vercel-labs/skills, verified 2026-11-03.
- https://github.com/supabase/agent-skills, verified 2026-11-03.
- https://github.com/anthropics/claude-plugins-official (`plugins/frontend-design`) and
  https://github.com/anthropics/skills (`skills/frontend-design`), verified 2026-11-03.
- https://github.com/vercel-labs/agent-skills (`skills/web-design-guidelines`) and https://vercel.com/design/guidelines,
  verified 2026-11-03.
- https://github.com/cloudflare/kumo (`skills/kumo-design`) and https://kumo-ui.com/skill, verified 2026-11-03.
- https://code.claude.com/docs/en/discover-plugins, verified 2026-11-03.
- The `claude-plugins-official` marketplace manifest (`.claude-plugin/marketplace.json`) and the `laravel-boost`
  and `context7` plugin directories in it, read 2026-11-03.
