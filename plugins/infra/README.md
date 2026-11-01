# infra

Failover for everything a product cannot lose: DNS, mail, hosting, the database and object storage.

## Skills

| Skill | Use it when |
|---|---|
| `high-availability` | designing or reviewing failover, backups and restores for DNS, mail, hosting, PostgreSQL or object storage |

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install infra@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it.

## How rules are tagged

Rules marked `[invariant]` hold in every project. Rules marked `[default]` hold unless the project records a
different choice in an ADR that names the trade-off.
