# saas

Decisions for multi-tenant B2B SaaS that are expensive to change later: how records are identified, how tenant
data stays apart on every path, how permissions are granted, what to build and what to buy, how EU B2B billing
and GDPR duties turn into code and tests, and when work moves into a separate service.

Rules are stack-neutral where they can be. Laravel and PostgreSQL detail sits in each skill's `references/stack-*.md`,
and `service-boundaries` assumes a PHP or Laravel monolith.

## Skills

| Skill | Use it when |
|---|---|
| `dual-key-identifiers` | adding a model, route, API field, export, webhook or realtime channel that exposes an ID |
| `tenant-isolation` | data can cross a tenant boundary: web, API, jobs, schedules, caches, exports, notifications, realtime |
| `authorization-rbac` | designing or reviewing roles, permissions, owner rights, invitations or API token scopes |
| `build-vs-buy` | choosing between building in-house and a vendor or package, or adding a provider behind an adapter |
| `billing-eu-b2b` | touching checkout, subscriptions, invoices, VAT, reverse charge, webhooks from a payment provider, coupons or plan limits |
| `gdpr-engineering` | a change adds personal data, a third-party service, a retention period, or data leaving the EU/EEA |
| `service-boundaries` | someone proposes a microservice, worker or rewrite in another language, or designs the contract between services |

Legal and tax content is a review-ready draft for the DE/EU scope, not legal or tax advice.

Claude Code loads a skill when the task matches its description. You can also call one directly, for example
`/saas:tenant-isolation`.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install saas@rene-roscher-skills
```

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off). Project choices that are a matter of taste live in the example profile under
`templates/project-overlay/profiles/` at the repository root.

See [CHANGELOG.md](CHANGELOG.md) for changes.
