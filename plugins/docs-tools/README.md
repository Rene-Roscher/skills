# docs-tools

An optional plugin with no skills of its own. It declares one dependency, the `context7` plugin from the official
marketplace (`claude-plugins-official`), so installing `docs-tools` installs the Context7 documentation MCP server.

The `core` skills look for a documentation tool by capability. With Context7 present, `evidence-before-claims`
resolves the library ID, then queries the docs for the version in your lockfile. Without it, the skills fall back
to the vendor's documentation and mark anything they could not confirm as unverified. Installing this plugin is
recommended but not required.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install docs-tools@rene-roscher-skills
```

## What gets installed

The `context7` plugin connects to Context7's hosted MCP server over HTTPS and works without an account. Its
tools are `resolve-library-id` and `query-docs`. Queries you send to it leave your machine, so keep secrets and
private code out of them.

Sources, verified 2026-10-31:
- https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json (the
  `context7` entry and its hosted server)
- https://github.com/upstash/context7 (tool names)

If you already have `context7` installed and enabled from the official marketplace, this plugin adds nothing.

See [CHANGELOG.md](CHANGELOG.md) for changes.
