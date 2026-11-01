# data

PostgreSQL in production: queries, indexes, migrations without downtime, pooling and the traps that only show on PostgreSQL.

## Skills

| Skill | Use it when |
|---|---|
| `postgres-production` | writing queries, adding indexes or constraints, planning a migration or backfill, or debugging a PostgreSQL-only failure |

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install data@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it.

## How rules are tagged

Rules marked `[invariant]` hold in every project. Rules marked `[default]` hold unless the project records a
different choice in an ADR that names the trade-off.
