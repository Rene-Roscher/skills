---
name: project-inception
description: "Sets up docs/ before any feature code: product, business and per-area specs, ADRs, plans, project facts and an AGENTS.md read-first table, each written with the skill that owns the area, gated on owner approval. Adopts undocumented repos by deriving specs from code and listing drift. Use when starting a new project or repo, or onboarding a codebase without docs. Not for single features or one ADR."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Project inception

This skill makes a project's `docs/` folder the first thing that exists. Product, business and every technical
area are evaluated and written down, each with the skill that owns the area, and the owner approves the result
before any feature code is written. For a repository that already has code and no docs, it derives the specs from
the code and lists every place where existing docs and code disagree. Single features are planned afterwards with
`feature-planning`. It prevents the project whose stack, tenancy model, ID format and price model were settled by
the first scaffold command, and the agent that reads a stale spec and builds against behaviour the code no longer
has.

## Applies when / does not apply

- Applies: a new project, product or repository; "set up the repo", "start a new app", "scaffold", "kick off",
  "bootstrap"; a codebase without docs that agents should work on; writing or repairing `AGENTS.md` or `CLAUDE.md`
  routing; an audit of the whole docs folder against the code.
- Does not apply: one feature in a project that already has approved docs (`feature-planning`), one ADR for one
  decision, a README fix, a single claim checked against a library or the code (`evidence-before-claims`), pricing
  alone (`pricing-and-unit-economics`).

## Rules

Most important first. Examples use a booking system for venues.

- [invariant] Inception gate: no feature code before the inception docs exist and the owner approved them. Until
  then, write only under `docs/`, plus `AGENTS.md`, `CLAUDE.md`, `README.md` and `.gitignore`. A framework
  scaffold, a package manifest, a CI workflow or infrastructure code are decisions (stack, hosting, delivery), so
  they wait too. A throwaway spike that answers one numbered open decision may live under `spikes/`, is named in
  that decision, and never becomes product code. Approval is recorded in the inception record
  (`docs/plans/YYYY-MM-DD-inception.md`) as `Status: Approved` with `Approved-by: [name], [date]`, after the owner
  approved in the conversation. "Just scaffold it" is not approval.
  Why: the first scaffold fixes the language, framework, database, tenancy shape and ID format before anyone
  weighed them, and each is expensive to change once data exists.
  Test: `python3 ${CLAUDE_SKILL_DIR}/scripts/check_docs.py --require-approved` exits 1 while the record says Draft
  (C13); eval `output-greenfield-gate` writes no source file.
  Source: plan-validate-execute, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  (verified 2026-10-31).
- [invariant] Each area document is written with the skill that owns the area, and says so. Load the owning skill
  from the table below before writing its document, answer that skill's decisions in the document, and list it on
  the `Skills:` header line. If the skill is not installed, use
  [references/area-checklists.md](references/area-checklists.md) and write `Skills: none installed, area checklist
  used`; the handover names those areas.
  Why: a spec written from general knowledge skips what the area skill exists for: the cross-tenant test, the
  internal ID in a URL, the VAT rule, the restore drill.
  Test: `check_docs.py` fails on a product, business or spec document without a `Skills:` line (C09).
  Source: reproducible with the test above.
- [invariant] Every area is answered: a document, or N/A with a reason specific to this project, in the areas table
  of the inception record ("N/A: single-tenant internal tool, one customer"). "Later" and "TBD" are not answers;
  each becomes a tracked issue with a link.
  Why: an area nobody wrote down is an area the first feature decides by accident.
  Test: every row of the areas table has a document link or an N/A reason; review rejects a bare N/A.
  Source: same rule as the plan sections in `feature-planning`.
- [invariant] Decisions belong to the owner. Stack, hosting region, tenancy model, ID format, pricing model, legal
  scope, build or buy: collect them as a numbered list in the inception record, each with options, trade-offs and
  one recommendation. Format as in `feature-planning` (Open decisions). Settled decisions become ADRs.
  Why: numbered items let the owner answer in one line, and a choice made inside a scaffold is invisible.
  Test: `check_docs.py` fails when Open decisions is missing or an item has no `Recommendation:` line (C12).
  Source: reproducible with the test above.
- [invariant] A read-first routing table tells agents which document to open for which task. It lives in
  `AGENTS.md` at the root (or in `CLAUDE.md`), has the columns Task, Read first and Skill, names every spec, and
  every path in it exists. Write paths in backticks.
  Why: an agent that does not find the spec guesses, and a table entry pointing at a renamed file sends it nowhere.
  Test: `check_docs.py` fails on a missing table (C04) or a path that does not exist (C05) and warns on a spec no
  row names (C06).
  Source: AGENTS.md, "Create an AGENTS.md file at the root of the repository" (https://agents.md/, verified
  2026-10-31).
- [invariant] When both files exist, `CLAUDE.md` imports `@AGENTS.md` on a line of its own, outside backticks, or
  holds the routing table itself.
  Why: by default Claude Code reads `AGENTS.md` only when there is no `CLAUDE.md` in the working directory or above
  it, so the table is silently ignored.
  Test: `check_docs.py` fails when `AGENTS.md` holds the table, a `CLAUDE.md` exists and no import is present
  (C07); eval `output-routing-claude-md-import`.
  Source: https://code.claude.com/docs/en/memory, "By default, Claude reads `AGENTS.md` only when you have no
  `CLAUDE.md` in your working directory or above it" and "Keeping the import never makes Claude read `AGENTS.md`
  twice" (verified 2026-10-31).
- [invariant] Adopting an existing repository: derive the specs from the code. Each statement in an as-built spec
  comes from code, schema, config, routes, jobs or CI, with its `path:line`, and is labelled verified, reported or
  inferred as `evidence-before-claims` defines them. Old docs, tickets and subagent reports are reported until
  read in the code. The spec header names the code it describes (`Code:`) and the date it was checked. Sources of
  facts: [references/adoption.md](references/adoption.md).
  Why: a plan built on unchecked reports carried many errors, including wrong statements about the project's own
  code; comparing one document with another finds none of them.
  Test: `check_docs.py` fails when a `Code:` path matches nothing (C10) or has no check date (C11).
  Source: reproducible with the test above.
- [invariant] Drift is recorded, never resolved silently. When a document and the code disagree, add a row to the
  drift table in the inception record: claim with its location, what the code does with `path:line`, which side
  runs today, and the resolution. The as-built spec describes what runs. When the document states intent (a
  price, a contract or privacy promise, a security property, a limit), the code may be the bug: the row becomes a
  numbered open decision, and neither side is changed until the owner answers.
  Why: rewriting the doc to match the code can erase the one record of what was promised; changing the code to
  match the doc can break customers who rely on what runs.
  Test: eval `adversarial-spec-code-drift`: a doc says tokens expire after 30 days, the code uses 90; the reply
  names both values with locations, asks the owner, and edits no code.
  Source: reproducible with the test above.
- [invariant] Specs change in the same change as the code they describe. A change that alters behaviour under a
  spec's `Code:` paths updates the spec, or its description says why the spec is unaffected.
  Why: a spec that is right on the day it was written and wrong a month later is worse than none, because agents
  trust it.
  Test: `git diff --name-only [base]...HEAD | python3 ${CLAUDE_SKILL_DIR}/scripts/check_docs.py --changed -` reports
  each spec whose code changed without it (C15); CI runs it with `--strict`.
  Source: Google engineering practices, Documentation: "If a CL changes how users build, test, interact with, or
  release code, check to see that it also updates associated documentation"
  (https://google.github.io/eng-practices/review/reviewer/looking-for.html, verified 2026-10-31).
- [default] Docs tree: `docs/product/`, `docs/business/`, `docs/specs/[area].md`, `docs/adr/NNNN-[slug].md`,
  `docs/plans/YYYY-MM-DD-[slug].md` and `docs/PROJECT-FACTS.md`, plus a `docs/README.md` that says which files are
  binding (specs, ADRs, project facts) and which are dated snapshots (finished plans, research, audits). Layout
  and templates: [references/docs-tree.md](references/docs-tree.md).
  Trade-off: fixed names instead of the team's own; `check_docs.py --docs specs` accepts another root folder.
  Deviate only with an ADR that names this trade-off.
  Proof: `check_docs.py` passes on the tree (C01, C02).
- [default] Each product, business and spec document starts with a header block: `Status:` (Draft, Approved,
  Implemented, Superseded by [link]), `Owner:`, `Skills:`, `Code:` (paths or globs, or `none yet`) and `Checked
  against code: YYYY-MM-DD`.
  Trade-off: five lines to keep current per document, in exchange for a mechanical drift check. Deviate only with
  an ADR that names this trade-off.
  Proof: `check_docs.py` checks Status, Skills, Code and the date (C09 to C11).
- [default] The routing file stays short and points; it does not restate specs. Keep it under 200 lines, and do
  not `@`-import specs into it.
  Trade-off: one more file to open per task, in exchange for a file that is read in full every session. Deviate
  only with an ADR that names this trade-off.
  Source: https://code.claude.com/docs/en/memory: "target under 200 lines per CLAUDE.md file. Longer files consume
  more context and reduce adherence", and imports "don't reduce its context cost" (verified 2026-10-31).
- [default] ADRs follow Nygard's format: title, context, decision, status, consequences; one or two pages;
  numbered sequentially, numbers never reused; a reversed decision is marked superseded, not deleted. ADR 0001
  records the decision to keep ADRs.
  Trade-off: a file per decision. Deviate only with an ADR that names this trade-off.
  Source: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions ("ADRs will be numbered
  sequentially and monotonically. Numbers will not be reused."), verified 2026-10-31. `check_docs.py` fails on a
  reused number (C14).

## Which skill feeds which document

Load the skill, answer its decisions in the document, put its name on the `Skills:` line. A skill named here may
live in another plugin of this marketplace; questions per area are in
[references/area-checklists.md](references/area-checklists.md).

| Document | Skills | Decides |
|---|---|---|
| `docs/product/brief.md` | `product-strategy` | problem, buyer and personas, today's workaround, market, positioning, non-goals, success metric, moment of highest stress |
| `docs/business/model.md` | `pricing-and-unit-economics`, `build-vs-buy` | price model and axes, cost per customer, margin floor, who the buyer is (B2B or B2C), markets, what is bought |
| `docs/specs/architecture.md` | `service-boundaries`, `web-architecture` | deployables, contracts, public pages vs app, rendering per surface |
| `docs/specs/data.md` | `dual-key-identifiers`, `postgres-production` | database engine, ID format, migration and backfill policy |
| `docs/specs/tenancy.md` | `tenant-isolation` | tenant model, scoping per surface, cross-tenant tests |
| `docs/specs/access.md` | `authorization-rbac` | roles, owner rule, invitations, API token scopes |
| `docs/specs/billing.md` | `billing-eu-b2b` | provider, invoices, VAT, webhooks, limits |
| `docs/specs/privacy.md` | `gdpr-engineering` | data inventory, processors, retention, region |
| `docs/specs/availability.md` | `high-availability` | recovery targets, backups, restore drills, failover per dependency |
| `docs/specs/delivery.md` | `github-actions-hardening`, `container-images`, `safe-actions` | CI, images, release, what needs approval |
| `docs/specs/testing.md` | `verify-before-done`, `browser-verification`, `feature-delivery` | test lanes, production engine in tests, definition of done |
| `docs/specs/api.md` | `mcp-server-design` | public API and agent tools, when the product has them |
| `docs/specs/runtime.md` | `laravel-architecture`, `laravel-production-runtime` | stack rules, when the stack is Laravel |
| `docs/PROJECT-FACTS.md` | `evidence-before-claims`, `safe-actions` | versions from lockfiles, commands, providers, approval list |

## Procedure: new project

1. Search first: existing repos, docs, issues and cancelled decisions on the same product.
2. Create the inception record from [references/docs-tree.md](references/docs-tree.md) with `Status: Draft` and
   `Mode: new`. Create the folders.
3. Product, then business: load `product-strategy` and `pricing-and-unit-economics`; ask the owner what only the
   owner knows (buyer, budget, markets) and label market claims verified, reported or inferred.
4. Specs, area by area, each with its skill. Write `Code: none yet`. Record cross-area decisions as numbered open
   decisions, not as facts.
5. `docs/PROJECT-FACTS.md`, ADR 0001, `docs/README.md` with the binding-or-snapshot table.
6. Routing table in `AGENTS.md`; if a `CLAUDE.md` exists, import `@AGENTS.md` there.
7. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_docs.py` and fix every error. In clients that don't set
   `CLAUDE_SKILL_DIR`, the script is in this skill's `scripts/` folder; without Python, check the list in its
   `--help` text by hand.
8. Gate: hand over in the format below and stop. No scaffold, no commit of code, no push.
9. After approval: answers into the documents, settled decisions into ADRs, record set to Approved, then
   `check_docs.py --require-approved`. The scaffold follows the approved stack decisions (`stack-bootstrap`), and
   the first features each get a `feature-planning` plan.

## Procedure: adopting an existing repository

1. Inventory where the facts live (manifests and lockfiles, schema and migrations, routes, config, jobs and
   schedules, CI, infrastructure): [references/adoption.md](references/adoption.md).
2. Collect the existing docs, instruction files and READMEs. Treat every statement in them as reported.
3. Write as-built specs per area with `path:line` evidence and the `Code:` header; load the area skill and note
   where the code breaks its rules as findings, not as fixes.
4. Fill the drift table. Intent-carrying rows become numbered open decisions.
5. Routing table, project facts, `docs/README.md`; run `check_docs.py`.
6. Gate: hand over and stop. Bug and security fixes go through `bug-investigation` meanwhile; new features wait.

Handover format:

```text
Inception: docs/plans/2026-03-04-inception.md (Status: Draft, check_docs.py passes)
Mode: new. Areas: 11 written, 2 N/A with reasons (api, runtime).
Written without their skill: privacy (gdpr-engineering not installed).
Open decisions:
1. Tenancy: one database with a venue_group_id on every table, or a schema per tenant? Recommendation: ...
2. Hosting region: EU only? Recommendation: ...
Nothing outside docs/ and AGENTS.md was written. Reply with approval, or answer by number ("1 A, 2 yes").
```

## Traps

- "Just scaffold the app" or "start with the login page" is not approval. The scaffold is the stack decision.
- `AGENTS.md` and `CLAUDE.md` both present, the table only in `AGENTS.md`: Claude Code never sees it.
- `@docs/specs/billing.md` outside backticks in `CLAUDE.md` imports the whole spec into every session; inside
  backticks it is a plain path.
- A spec still marked Draft months after the feature shipped; the status line lies and agents treat it as a
  proposal.
- A finished build plan read as the spec. Plans are snapshots; the spec is the binding file.
- Checking docs against docs: two documents that agree can both be wrong. Check against code.
- Drift "fixed" by rewriting the doc to match the code when the doc held the promise and the code was the bug.
- Market sizes, competitor prices and conversion rates written as facts without a source.

## Done when

- `check_docs.py` passes, and `--require-approved` passes once the owner approved.
- Every area has a document or an N/A reason; every document names the skills it was written with.
- Open decisions are numbered with recommendations; answered ones are ADRs.
- The routing table names every spec and resolves; `CLAUDE.md` imports `@AGENTS.md` where both exist.
- In adoption mode, every drift row has a resolution or a decision number.

## References

- [references/docs-tree.md](references/docs-tree.md): load when creating the tree or any of its files: layout,
  header block, binding-or-snapshot table, templates for the inception record, brief, business model, spec,
  routing table and ADR.
- [references/area-checklists.md](references/area-checklists.md): load when writing an area document, especially
  when the owning skill is not installed.
- [references/adoption.md](references/adoption.md): load when the repository already has code: where facts live,
  as-built spec procedure, drift table, resolution rules.
- [references/keeping-specs-true.md](references/keeping-specs-true.md): load when wiring the drift check into CI
  or a PR template, or when a spec's status or check date is stale.
- `${CLAUDE_SKILL_DIR}/scripts/check_docs.py`: run before handover and in CI. `--help` lists checks C01 to C15;
  `--self-test` runs its fixtures.

## Sources

- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices: plan-validate-execute, a plan
  file validated by a script before execution; verified 2026-10-31.
- https://agents.md/: `AGENTS.md` at the repository root; "The closest AGENTS.md to the edited file wins";
  verified 2026-10-31.
- https://code.claude.com/docs/en/memory: `AGENTS.md` is read only without a `CLAUDE.md`; `@path` imports, code
  spans not imported; CLAUDE.md under 200 lines; verified 2026-10-31.
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions: ADR sections, numbering, superseded
  decisions, one or two pages; verified 2026-10-31.
- https://adr.github.io/: an ADR "captures a single AD and its rationale"; the collection is the decision log;
  verified 2026-10-31.
- https://google.github.io/eng-practices/review/reviewer/looking-for.html: a change updates its documentation;
  verified 2026-10-31.
