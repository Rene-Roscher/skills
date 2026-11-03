# infra

Infrastructure changes, workloads, the TLS edge, alerting and recovery, and failover for everything a product cannot lose.

## Skills

| Skill | Use it when |
|---|---|
| `high-availability` | designing or reviewing failover, backups and restores for DNS, mail, hosting, PostgreSQL or object storage |
| `infrastructure-as-code` | writing or reviewing OpenTofu, Ansible, SOPS with age, or Flux and Argo CD config |
| `kubernetes-workloads` | writing or reviewing Deployments, Jobs, namespaces, NetworkPolicies, Helm charts or Kustomize overlays |
| `edge-proxy-tls` | configuring a Caddy edge, on-demand TLS for customer domains, forwarded headers, rate limits and edge caching |
| `observability-and-dr` | writing alert rules, routing, dashboards, logging and error-tracker config, restore drills, runbooks or postmortems |

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install infra@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it.

## How rules are tagged

Rules marked `[invariant]` hold in every project. Rules marked `[default]` hold unless the project records a
different choice in an ADR that names the trade-off.
