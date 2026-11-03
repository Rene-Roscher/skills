# skills

Engineering skills for coding agents, packaged as a Claude Code plugin marketplace. The skills follow the
[Agent Skills](https://agentskills.io/specification) format, so the same folders work in other agents that read
it. They cover habits that hold for any stack (check facts against a source, prove work before calling it done,
ask before actions that leave the machine) and decisions for multi-tenant B2B SaaS, Laravel, web front ends and
delivery pipelines.

Each skill keeps the decision, the rule and the trap. Syntax that a vendor already documents is linked, not
copied.

## Install

In a Claude Code session:

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install core@rene-roscher-skills
/plugin install saas@rene-roscher-skills
```

From a shell:

```bash
claude plugin marketplace add Rene-Roscher/skills
claude plugin install core@rene-roscher-skills
```

Install the `laravel` plugin at project scope (`--scope project`) and only in Laravel projects. Its README
explains why.

Claude Code does not auto-update third-party marketplaces by default. Turn it on under `/plugin`, then
Marketplaces, or run `claude plugin update core@rene-roscher-skills`.

## Plugins

| Plugin | What it decides | Skills |
|---|---|---|
| [core](plugins/core/README.md) | How an agent checks facts, verifies work, handles risky actions, plans, investigates, tests, writes maintainable code, keeps lessons, stays on the goal, delegates to subagents and commits. Any stack. | `goal-focus`, `agent-delegation`, `evidence-before-claims`, `verify-before-done`, `safe-actions`, `feature-planning`, `feature-delivery`, `bug-investigation`, `project-inception`, `learning-loop`, `test-strategy`, `maintainable-code`, `agent-toolbelt`, `commit-hygiene`, `stack-bootstrap`, `performance-gate` |
| [saas](plugins/saas/README.md) | Tenancy model, IDs, tenant isolation, permissions, plan limits and overrides, build or buy, EU B2B billing, GDPR duties, service boundaries, jobs, outbound requests and webhooks, and the EU and German legal baseline. | `tenancy-model`, `dual-key-identifiers`, `tenant-isolation`, `authorization-rbac`, `plan-entitlements`, `build-vs-buy`, `billing-eu-b2b`, `gdpr-engineering`, `service-boundaries`, `async-reliability`, `egress-and-webhooks`, `eu-de-legal-baseline` |
| [laravel](plugins/laravel/README.md) | Laravel structure and the gaps between a green test suite and production. | `laravel-architecture`, `laravel-production-runtime` |
| [web](plugins/web/README.md) | Where public pages and dashboards live, how they render, what good UI looks like and how UI changes are proven. | `web-architecture`, `vue-inertia-frontend`, `design-quality`, `browser-verification` |
| [delivery](plugins/delivery/README.md) | The local Docker Compose stack, GitHub Actions hardening, container image baselines and signed releases. | `local-dev-stack`, `github-actions-hardening`, `container-images`, `release-supply-chain` |
| [business](plugins/business/README.md) | Product discovery, a dated market analysis, pricing from unit costs, and copy that reads as written by a person. | `product-strategy`, `market-analysis`, `pricing-and-unit-economics`, `human-copy` |
| [data](plugins/data/README.md) | PostgreSQL in production: queries, indexes, migrations without downtime, pooling. | `postgres-production` |
| [infra](plugins/infra/README.md) | Infrastructure as code, Kubernetes workloads, the edge proxy, observability and DR, and failover for DNS, mail, hosting, the database and object storage. | `infrastructure-as-code`, `kubernetes-workloads`, `edge-proxy-tls`, `observability-and-dr`, `high-availability` |
| [api](plugins/api/README.md) | Public REST API contracts, and MCP servers that agents use safely on multi-tenant products. | `api-contract`, `mcp-server-design` |
| [go](plugins/go/README.md) | Production Go services and wire contracts shared across languages. | `go-service-baseline`, `cross-service-contracts` |
| [media](plugins/media/README.md) | Short product videos: the plan and approval gate, then build, voice, sound, master and delivery with measured checks. | `video-planning`, `video-production` |
| [docs-tools](plugins/docs-tools/README.md) | Optional. Installs the Context7 documentation MCP server that `core` uses when present. | none |

Skills are called with the plugin name as prefix, for example `/saas:tenant-isolation`. Most of the time you
don't call them: Claude Code loads a skill when the task matches its description.

## How rules are tagged

Every rule in a skill carries one of two tags.

- `[invariant]`: never deviate. These cover security, correctness, data loss, and the gates a workflow skill is
  built around. Each one has a test you can run.
- `[default]`: the recommended choice. Deviate only with an ADR (architecture decision record) that names the
  trade-off the rule lists.

Choices that are a matter of taste or of one project are not rules. They live in
[templates/project-overlay/profiles/example-laravel-saas.md](templates/project-overlay/profiles/example-laravel-saas.md),
an example profile you can copy and change.

Every rule has a source: a vendor document or specification with the date it was checked, or a test that
reproduces the behaviour.

## Pin a version for a team

Commit a `.claude/settings.json` to the project. [templates/claude-settings.team.json](templates/claude-settings.team.json)
is a starting point:

```json
{
  "extraKnownMarketplaces": {
    "rene-roscher-skills": {
      "source": {
        "source": "github",
        "repo": "Rene-Roscher/skills",
        "ref": "core--v0.1.0"
      }
    }
  },
  "enabledPlugins": {
    "core@rene-roscher-skills": true,
    "saas@rene-roscher-skills": true,
    "laravel@rene-roscher-skills": true
  }
}
```

- Releases are tagged per plugin as `<plugin>--v<version>`. Pinning `ref` to any tag pins the whole catalog at
  that commit, because one marketplace serves one version of each plugin. Use a tag that exists, and upgrade by
  changing `ref` in a reviewed pull request.
- Marketplace sources accept a branch or tag in `ref`, not a commit SHA.
- Claude Code applies `extraKnownMarketplaces` from a repository only after the folder is trusted. Until then it
  ignores the entry without a message.
- In `-p` runs and CI, set `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` so the first turn waits for plugin installs.
- One person can opt out of a project-enabled plugin by setting it to `false` in `.claude/settings.local.json`.

The template also carries permission rules: reads of `.env` files and key files are denied, and `git push` and
destructive commands ask first. Bash rules match the command as written, so treat them as a safety net, not as
the only control.

Sources: https://code.claude.com/docs/en/plugins/marketplace-reference,
https://code.claude.com/docs/en/settings-reference, https://code.claude.com/docs/en/permissions (verified
2026-10-31).

For agents that read `AGENTS.md`, [templates/AGENTS.md](templates/AGENTS.md) holds the core working rules in
under 60 lines, plus a map from project stack to plugin.

## Use with other agents

The skill folders follow the Agent Skills specification. The `core` and `saas` skills use only the fields the
specification defines. The stack skills add one Claude Code field, `paths`, which loads a skill only when
matching files are in play. Claude.ai uploads and the Skills API reject that field, and other clients may
ignore or reject it.

The [`skills` CLI](https://github.com/vercel-labs/skills) installs skills into the project folders of many
agents (Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode and others). It needs Node.js 22.20 or later:

```bash
DISABLE_TELEMETRY=1 npx skills@1.7.4 add Rene-Roscher/skills --skill evidence-before-claims
```

That CLI collects anonymous usage data. For repositories that GitHub confirms are public, it sends the
repository and skill identifiers. Setting `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` turns off both the telemetry
and its security-audit requests. Pin a version as above instead of running whatever is latest. The skills here
sit under `plugins/*/skills/`, outside the CLI's standard locations, so it finds them through its fallback
recursive search. Sources: the CLI's README and `docs/creating-skills.md` (verified 2026-10-31).

## What a plugin can do

A plugin runs with your user's privileges. Hooks, MCP servers and executables a plugin ships run outside the
sandbox, and skills enter the agent's context as instructions. The plugins in this repository ship skills only:
no hooks, no MCP servers of their own, no executables. `docs-tools` and `laravel` declare dependencies on plugins
from the official marketplace, which do add MCP servers. The lint in `tools/` checks that no plugin adds hooks,
`bin/` or an MCP configuration. Source: https://code.claude.com/docs/en/plugins/security (verified 2026-10-31).

## Contributing, security, license

- [CONTRIBUTING.md](CONTRIBUTING.md): authoring rules, evals, checks to run, commit messages.
- [SECURITY.md](SECURITY.md): how to report a vulnerability.
- [LICENSE](LICENSE): Apache License 2.0. See also [NOTICE](NOTICE).
