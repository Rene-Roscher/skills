# Team settings for plugins

How the committed `.claude/settings.json` carries the plugin setup, how a teammate gets it, and how a re-run
changes it.

## Example

A Laravel application with PostgreSQL, Redis and GitHub Actions. The `ref` pins this marketplace to a release tag;
use the tag format of the marketplace's releases.

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
    "docs-tools@rene-roscher-skills": true,
    "laravel@rene-roscher-skills": true,
    "data@rene-roscher-skills": true,
    "delivery@rene-roscher-skills": true,
    "laravel-boost@claude-plugins-official": true,
    "redis-development@claude-plugins-official": true
  }
}
```

The repository's `templates/claude-settings.team.json` adds a permissions block (deny reads of secrets, ask before
destructive commands). Merge it when the project has no permissions yet.

## Merge rules

- Read the existing file first. Add keys; never drop keys the bootstrap did not write (`permissions`, `hooks`,
  `env`, `model`).
- `enabledPlugins` entries are `name@marketplace` with `true`. A plugin whose signal is gone becomes `false` with a
  note in the report, or is removed after the owner agrees.
- Settings files are strict JSON: no comments, no trailing commas. Validate after writing, for example with
  `python3 -m json.tool .claude/settings.json`.
- Lists such as `permissions.allow` merge across scopes; a teammate's local file adds to them and cannot remove the
  project's `deny` or `ask` rules.

## Teammate onboarding

Put these lines in the project's agent docs (`AGENTS.md`, `CLAUDE.md` or the README), one install line per plugin
in `enabledPlugins`:

```text
# once per machine, from the repository root
claude plugin marketplace add anthropics/claude-plugins-official   # only if no interactive session has run yet
claude plugin install core@rene-roscher-skills --scope project
claude plugin install laravel-boost@claude-plugins-official --scope project
# ... one line per enabled plugin
```

Then start a session in the repository, accept the folder trust prompt (the marketplace declaration and project
allow rules wait for it), and check `/plugin` on the Installed tab.

## Re-running after a stack change

1. Run detection again and diff the result against `enabledPlugins`.
2. New signal: add the plugin, install it, add its install line to the docs.
3. Lost signal: disable the plugin at project scope and remove its install line, after the owner agrees.
4. Laravel: after `composer update`, run `php artisan boost:update` (or keep it in `post-update-cmd`) and review the
   diff of the generated files.
5. Report the change set: added, disabled, unchanged, each with its evidence path.

## Sources

- https://code.claude.com/docs/en/settings: scopes, lists merge, keys that wait for trust, strict JSON, verified
  2026-11-03.
- https://code.claude.com/docs/en/discover-plugins: project scope writes `.claude/settings.json`, collaborators
  install once, verified 2026-11-03.
