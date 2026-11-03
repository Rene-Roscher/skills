# api

Public interfaces of a product: REST API contracts (versioning, errors, pagination, idempotency, deprecation, parity) and MCP servers that agents can use safely.

## Skills

| Skill | Use it when |
|---|---|
| `mcp-server-design` | building or reviewing an MCP server, its tools, their descriptions, results, errors and safety rules |
| `api-contract` | adding or changing a public REST endpoint, field, error, list, token scope, rate limit or deprecation |

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install api@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it.

## How rules are tagged

Rules marked `[invariant]` hold in every project. Rules marked `[default]` hold unless the project records a
different choice in an ADR that names the trade-off.
