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
| `build-vs-buy` | choosing between building in-house and a vendor or package, checking a package's reach and maintenance with `dep_health.py`, or adding a provider behind an adapter |
| `tenancy-model` | designing organizations, teams, projects, memberships, invitations or ownership transfer |
| `plan-entitlements` | adding a plan limit or feature flag per plan, a per-tenant override, an add-on, or enforcing a quota |
| `billing-eu-b2b` | touching checkout, subscriptions, invoices, VAT, reverse charge, webhooks from a payment provider or coupons |
| `gdpr-engineering` | a change adds personal data, a third-party service, a retention period, or data leaving the EU/EEA |
| `eu-de-legal-baseline` | a change touches EU or German law beyond GDPR: Impressum, cookies, consumer sign-up, AGB, marketing claims, accessibility, user content, NIS2, AI features, retention |
| `domain-design` | deciding where code lives in a long-lived product: bounded contexts and the context map, aggregates and invariants, domain and integration events, long-running flows, and when plain CRUD is enough |
| `service-boundaries` | someone proposes a microservice, worker or rewrite in another language, or designs the contract between services |
| `async-reliability` | adding or reviewing a job, consumer, scheduled task or notification, or a queue, retry or kill-switch setting |
| `egress-and-webhooks` | fetching a URL a user supplied, sending webhooks to customers, or receiving webhooks from providers |

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
