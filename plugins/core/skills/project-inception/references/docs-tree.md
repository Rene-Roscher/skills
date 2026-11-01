# Docs tree and templates

## Contents

- Layout
- Header block
- Binding or snapshot
- Inception record
- Product brief
- Business model
- Area spec
- Routing table
- ADR
- Project facts

Replace every `[placeholder]`. Keep each document to what an agent or the owner needs to decide or build; depth
goes into the area spec, not the routing file.

## Layout

```text
AGENTS.md                      routing table: task, read first, skill
CLAUDE.md                      optional; first line @AGENTS.md when both exist
docs/
  README.md                    what lives where; binding or snapshot
  PROJECT-FACTS.md             versions, commands, providers, approval list
  product/brief.md             problem, buyers, non-goals, success metric (plus market.md,
                               positioning.md, assumptions.md when product-strategy writes them)
  business/model.md            price model, unit economics, markets, build or buy
  specs/[area].md              one per area: architecture, data, tenancy, access, billing, privacy, ...
  adr/0001-record-architecture-decisions.md
  adr/NNNN-[slug].md
  plans/YYYY-MM-DD-inception.md
  plans/YYYY-MM-DD-[feature].md written by feature-planning
```

Area names are short nouns. One area, one file. A spec that grows past what one reader holds in mind splits by
sub-area (`billing.md`, `billing-invoices.md`), and each part gets its own routing row.

## Header block

Every document in `product/`, `business/` and `specs/` starts with:

```markdown
# Billing

Status: Draft
Owner: [name or role]
Skills: billing-eu-b2b, tenant-isolation
Code: src/billing/**, migrations/*invoice*
Checked against code: 2026-03-04
```

- `Status`: Draft (not approved), Approved (approved, not built), Implemented (code matches), Superseded by [link].
- `Skills`: the skills loaded while writing, or `none installed, area checklist used`.
- `Code`: comma-separated paths or globs relative to the repository root, or `none yet` before code exists.
  `check_docs.py` fails when an entry matches nothing, and uses the entries to find code changes without spec
  changes.
- `Checked against code`: the date someone last read the code against this spec. Required once `Code` names paths.

## Binding or snapshot

`docs/README.md` holds this table. Agents edit binding files; snapshots are dated and stay as they were.

```markdown
| Path | Kind | Updated when |
|---|---|---|
| `docs/specs/` | binding | in the same change as the code it describes |
| `docs/adr/` | binding, append-only | a decision is made or superseded |
| `docs/PROJECT-FACTS.md` | binding | a version, command, provider or approval changes |
| `docs/product/`, `docs/business/` | binding | the owner changes direction |
| `docs/plans/` | snapshot after delivery | never; a new plan supersedes |
| `docs/research/`, `docs/audits/` | snapshot | never; dated |
```

## Inception record

`docs/plans/YYYY-MM-DD-inception.md`. The script reads `Status`, `Approved-by` and the Open decisions section.

```markdown
# Inception: [project name]

Status: Draft
Approved-by:
Mode: new
Date: [YYYY-MM-DD]

## Summary
[Three sentences: what the product is, for whom, what the first release does.]

## Areas
| Area | Document | Status | Skills | N/A reason |
|---|---|---|---|---|
| Product | `docs/product/brief.md` | Draft | product-strategy | |
| Tenancy | `docs/specs/tenancy.md` | Draft | tenant-isolation | |
| API | | | | N/A: no public API in the first release; tracked in [issue link] |

## Drift
(Adoption mode only.)
| # | Document says | Location | Code does | Location | Runs today | Resolution |
|---|---|---|---|---|---|---|

## Open decisions
1. [Question answerable with a letter or yes/no]
   - Options: A, [...]; B, [...].
   - Trade-offs: [cost, reversibility, effort, risk].
   - Recommendation: [A], because [...].

## First features
- [Feature] → `feature-planning` plan after approval.
```

When the owner answers, add `Answer: B` under the item, copy lasting decisions into ADRs, then set
`Status: Approved` and `Approved-by: [name], [date]`.

## Product brief

`docs/product/brief.md`, written with `product-strategy`. When that skill is installed, its template and checker
define the product files; add the header block above them. The outline below is the fallback for one file:

```markdown
## Problem
[The problem without a solution in it.]
## Buyers and users
[Who pays, who uses, who decides. Personas with their job.]
## Today
[What they do now and what it costs them.]
## Market
[Alternatives they use; each claim labelled verified, reported or inferred, with a source.]
## Positioning
[Why this product over the alternatives, in one paragraph.]
## Non-goals
[What the first release will not do.]
## Success metric
[One number and its target date.]
## Moment of highest stress
[When the product is used under the most pressure; for a booking system, the minute a sold-out event opens.]
```

## Business model

`docs/business/model.md`, written with `pricing-and-unit-economics` and `build-vs-buy`:

```markdown
## Buyer and market
[B2B or B2C, countries, languages, currency.]
## Price model
[Axes that scale with value; free tier or not. Concrete prices are open decisions until the owner sets them.]
## Cost per customer
[Hosting, paid messages, payment fees, support; the driver of each.]
## Margin floor
[The rule that a plan must meet, as a formula.]
## Build or buy
| Capability | Build or buy | Vendor or package | Exit path |
|---|---|---|---|
## Legal scope
[Contracts, invoices, data protection obligations that follow from the buyer and markets; hand details to the
billing and privacy specs.]
```

## Area spec

```markdown
# [Area]

[Header block]

## Purpose
[What this area guarantees, in two sentences.]
## Rules
[The decisions from the owning skill, as this project applies them. Link ADRs.]
## Model
[Entities, states, ownership; tables or diagrams.]
## Interfaces
[Routes, events, jobs, contracts this area exposes or consumes.]
## Tests that prove it
[The guard tests: cross-tenant, ID leak, VAT cases, restore drill.]
## Open points
[Linked issues only.]
```

## Routing table

In `AGENTS.md` at the root. Paths in backticks so `CLAUDE.md` does not import them.

```markdown
## Read first

Read the listed document before changing code in that area. Code outranks docs; report drift.

| Task | Read first | Skill |
|---|---|---|
| New feature or product change | `docs/product/brief.md`, then a plan | `feature-planning` |
| Migration, model, new table | `docs/specs/data.md` | `dual-key-identifiers` |
| Anything a tenant can reach | `docs/specs/tenancy.md` | `tenant-isolation` |
| Roles, invitations, tokens | `docs/specs/access.md` | `authorization-rbac` |
| Checkout, invoices, plan limits | `docs/specs/billing.md` | `billing-eu-b2b` |
| New personal data, vendor or retention | `docs/specs/privacy.md` | `gdpr-engineering` |
| CI, images, release | `docs/specs/delivery.md` | `github-actions-hardening` |
| Commands, versions, providers | `docs/PROJECT-FACTS.md` | `evidence-before-claims` |
```

When a `CLAUDE.md` exists, its first line is `@AGENTS.md`. Project-only instructions follow below it.

## ADR

`docs/adr/NNNN-[slug].md`, after Nygard. One or two pages.

```markdown
# NNNN. [Short noun phrase]

Status: Accepted
Date: [YYYY-MM-DD]
Supersedes: [link or none]

## Context
[The forces: technical, product, legal, team.]
## Decision
[What we do, in active voice.]
## Consequences
[What becomes easier, what becomes harder, what we give up. Name the trade-off.]
```

ADR 0001 records the decision to keep ADRs. A reversed decision gets a new ADR; the old one is set to
`Superseded by [link]` and stays.

## Project facts

`docs/PROJECT-FACTS.md` holds facts, not rules: stack and the file that pins each version, commands (local stack,
tests on the production database engine, lint, build), local ports, queues and what each carries, providers with
their test modes, the approval list for actions that leave the machine, tracker and branch policy, and where
plans and ADRs live. The marketplace repository ships a fuller template under
`templates/project-overlay/PROJECT-FACTS.md`.
