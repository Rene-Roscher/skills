# api

Building MCP servers that agents can use safely: tenant binding, live permissions, tool design, confirmation for side effects and evals.

## Skills

| Skill | Use it when |
|---|---|
| `mcp-server-design` | building or reviewing an MCP server, its tools, their descriptions, results, errors and safety rules |

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install api@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it.

## How rules are tagged

Rules marked `[invariant]` hold in every project. Rules marked `[default]` hold unless the project records a
different choice in an ADR that names the trade-off.
