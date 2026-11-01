# Area checklists

## Contents

- How to use this file
- Product
- Business
- Architecture
- Data and identifiers
- Tenancy
- Access
- Billing
- Privacy
- Availability
- Delivery
- Testing
- API and agent tools
- Project facts

## How to use this file

Load the owning skill first; it carries the rules, sources and tests. This file lists the questions each area
document must answer, so that an area written without its skill still covers the same ground. Each answer is a
decision (into the spec), an open decision for the owner (numbered, in the inception record) or N/A with a reason.

## Product

Skill: `product-strategy`.
- Which problem, stated without a solution? Who pays, who uses, who decides?
- What do they do today, and what does that cost them in time or money?
- Which alternatives exist, and why would a buyer switch? Sources for every market claim.
- What will the first release not do?
- Which one number shows it works, and by when?
- When is the product used under the most pressure, and what must work then?

## Business

Skills: `pricing-and-unit-economics`, `build-vs-buy`.
- B2B, B2C or both? Which countries and currencies? This decides invoices, VAT and consumer law.
- Which axis scales with the value the customer gets (seats, usage, locations)? Free tier or trial?
- What does one customer cost per month, per driver? Which costs scale with usage you don't charge for?
- Which capabilities are bought (payments, mail, SMS, auth, search) and what is the exit path for each?

## Architecture

Skills: `service-boundaries`, `web-architecture`.
- How many deployables, and what measured reason justifies each one beyond the first?
- Which surfaces are public (marketing, docs, status pages) and do they fail independently of the app?
- Rendering per surface: server, client or prerendered. Typed routes, i18n, CSP.
- Contracts between components: format, versioning, who may break what.

## Data and identifiers

Skills: `dual-key-identifiers`, `postgres-production`.
- Production database engine and version; do tests run on the same engine?
- Internal keys and public IDs: format, generator, where translation happens.
- Migration policy: expand and contract, backfills, who may run them where.
- Time zones and money: storage type and rounding rule.

## Tenancy

Skill: `tenant-isolation`.
- What is a tenant, and is every row owned by exactly one?
- How does each surface scope: web, API, jobs, schedules, caches, exports, mails, webhooks, realtime, search?
- Which test proves tenant A cannot read or change tenant B's data, per surface?
- Single-tenant products answer N/A with the reason.

## Access

Skill: `authorization-rbac`.
- Roles and permissions; where checks run (server side only counts).
- Owner rights, transfer of ownership, last-owner protection.
- Invitations, removal, API tokens and their scopes, staff access and its audit trail.

## Billing

Skill: `billing-eu-b2b`.
- Payment provider and how its webhooks are processed (inbox, idempotency, re-fetch).
- Invoice numbering, VAT and reverse charge, e-invoice formats required in the markets.
- Plan limits: where they are enforced, and the error a customer sees at the limit.

## Privacy

Skill: `gdpr-engineering`.
- Inventory of personal data categories, purposes and legal bases.
- Processors and sub-processors; transfers outside the EU/EEA.
- Retention per category and the job that deletes; export and deletion on request.
- Review-ready draft, not legal advice; the owner or counsel signs off.

## Availability

Skill: `high-availability`.
- Recovery point and recovery time per component, as numbers.
- Backups: where, how often, encrypted, offsite; the last restore drill and its result.
- Failover for DNS, mail, hosting, database and object storage; what is single-homed and accepted as such.

## Delivery

Skills: `github-actions-hardening`, `container-images`, `safe-actions`.
- CI gates that block a merge; how actions and base images are pinned and updated.
- Release path from commit to production, rollback, and who approves what.
- Actions that need the owner's approval (production data, paid messages, deploys).

## Testing

Skills: `verify-before-done`, `browser-verification`, `feature-delivery`.
- Test lanes: fast lane, production-engine lane, browser checks; which ones gate a merge.
- What "done" means: the status ladder from implemented to live, and who may set each.
- Guard tests that run on every change (tenant isolation, ID leaks, permission matrix).

## API and agent tools

Skill: `mcp-server-design`, when the product exposes agent tools.
- Is there a public API in the first release? Parity with the UI, versioning, rate limits, plan gating.
- Agent tools: one connection, one tenant; previews and confirmation for actions that reach people.

## Project facts

Skills: `evidence-before-claims`, `safe-actions`.
- Versions read from lockfiles, not from memory.
- Commands to start, test, lint and build; where tests must run.
- Providers and their test modes; which local actions still reach real people.
