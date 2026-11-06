---
name: feature-planning
description: "Plans a feature end to end before any code and stops at a plan gate until the owner approves: business goal and problem, depth by stakes, a cost model for cost-intensive features, UX states, data model, permissions, tenant isolation, legal triggers, performance budget, failure modes, rollout, open decisions. Use when a new feature or product-visible change is requested, even a small one: let's build, add a, plan, design, spec out. Not for bug fixes or approved plans."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Feature planning

This skill turns a feature request into a written plan and stops there. The owner approves the plan and answers its
numbered open decisions before any code is written; `feature-delivery` then builds from the approved plan. It
prevents the "it's only small" feature that ships without tenant isolation, limits, API parity or a rollback, and
the product, price or legal choice that was settled inside an implementation the owner never saw.

## Applies when / does not apply

- Applies: any new feature or product-visible change, including small ones. "Let's build", "add a", "plan", "how
  should we implement", "design", "spec out", "write a design doc", "can you add".
- Does not apply: bug fixes (`bug-investigation`), refactors without behaviour change, executing a plan that is
  already approved (`feature-delivery`), running a command against a shared system (`safe-actions`), or a question
  about how a library or config behaves (`evidence-before-claims`).

## Rules

- [invariant] Plan gate: no build before an approved plan. For every new feature or product-visible change, write a
  plan from the template before writing code. Small features get short plans, not no plan. After writing it, stop:
  present it, and don't implement, commit or push. Building starts when the owner approves in the conversation and
  the plan header reads `Status: Approved` with `Approved-by:` filled.
  Why: features judged too small for a plan skipped tenant isolation, limits, API parity and rollback, and those
  gaps surfaced in production.
  Test: "Quick one: add a duplicate button. Just do it." leads to a plan file in the plans folder, no change under
  the source tree, and a reply that asks for approval (eval `adversarial-quick-feature-just-do-it`).
- [invariant] Every section answered. "Not applicable" needs a one-line reason specific to this feature ("N/A: the
  export streams existing rows, nothing new is stored"). "Later", "TBD" and "follow-up" are not answers: create a
  tracked issue with a priority and link it.
  Why: silent skipping is where cross-tenant leaks, missing indexes and missing customer docs come from. A written
  reason can be challenged; a missing section can't.
  Test: `python3 ${CLAUDE_SKILL_DIR}/scripts/lint_plan.py [plan]` fails on an empty section, a bare N/A, or a TBD
  without an issue link.
- [invariant] Problem before solution. Before any technology, write the problem with no solution in it, the
  business goal it serves (revenue, retention, cost or an obligation, with its source), the personas who have it, what they do today, the success moment from their view, a success metric, the non-goals,
  and the moment of highest stress in which the feature is used (for a booking system, the minute a sold-out event
  opens; for an invoicing app, month-end close). Questions that get there:
  [references/problem-framing.md](references/problem-framing.md).
  Why: a plan that covers only the calm path is unfinished, and B2B users judge a product at its moment of highest
  stress.
  Test: the linter fails when one of the eight fields in the Problem section is missing or empty.
- [invariant] Plan depth follows the stakes. The header sets `Tier:` and `Cost-intensive:` before the sections
  are written. `short` is for reversible changes with no new stored data, cost, money, auth or tenancy impact; it
  answers every section in a line. `standard` covers new data, endpoints, jobs or integrations. `full` is for
  anything cost-intensive, touching money, authentication or tenant isolation, irreversible, or carrying the
  business model; it measures on representative data where an estimate would decide, compares alternatives by
  cost, and gets one adversarial review. A feature is cost-intensive when it fans out to many sources or
  recipients, aggregates large data per request, calls paid APIs or sends paid messages, stores large volumes, or
  computes per request in a way that grows with tenant size; it is always `full` and carries a Cost model: cost
  per request and per tenant per month today, at 10x and at 100x, what is cached or precomputed, the budget, what
  happens when it is exceeded (limit, plan entitlement, degraded mode, kill switch), and the cost against what the
  tenant pays (`pricing-and-unit-economics` and `plan-entitlements`, plugins business and saas). Tier criteria:
  [references/plan-template.md](references/plan-template.md).
  Why: a uniform plan depth either buries a label change in ceremony or waves through a dashboard that queries
  ten sources per view; the expensive features are the ones whose cost decides whether a plan price holds, and
  that cost is cheapest to change before code exists.
  Test: `lint_plan.py` fails (P16) without a tier and a cost flag, and (P17) on a cost-intensive plan that is not
  `full`, lacks the Cost model or leaves a cost field without a number (eval
  `output-cost-intensive-dashboard-plan`).
- [invariant] Decisions belong to the owner: number them and recommend. Product, pricing, legal, scope and
  hard-to-reverse architecture questions are the owner's. Collect them as a numbered list at the end of the plan.
  Each item gives the options, the trade-offs (cost, reversibility, effort, risk) and one recommended default with
  its reason. Don't settle them implicitly in the design. Format:
  [references/open-decisions.md](references/open-decisions.md).
  Why: numbered items let the owner answer in one line ("1 yes, 2 B"), and an option list without a recommendation
  hands the work back.
  Test: the linter fails when Open decisions is not a numbered list or an item has no `Recommendation:` line (eval
  `output-usage-pricing-decisions-open`).
- [invariant] Failure-mode table, including what is irreversible or costs money. Columns Failure, Impact,
  Detection, Reaction. Cover at least a dependency that is down, the feature's own component failing, partial data,
  retries and duplicates, permission denied, limit reached and bulk scale. Below the table, list what is
  irreversible and what costs money or reaches people if it fires wrongly. Categories:
  [references/failure-modes.md](references/failure-modes.md).
  Why: scale, isolation and cost errors are cheapest to catch before code exists.
  Test: the linter fails without the table header or with fewer than three rows.
- [invariant] Tenant isolation is planned per surface, with a cross-tenant test. In a multi-tenant product, state
  for each surface how tenant A is kept from reading or changing tenant B's data: UI, API, exports, webhooks, public
  pages, realtime channels, cache keys, search, background jobs, admin views. The test plan has a cross-tenant test
  for every new resource. A single-tenant product answers N/A with the reason. The isolation rules themselves are in
  `tenant-isolation` (saas plugin).
  Why: leaks hide in the surfaces nobody listed: an export, a cached fragment, a broadcast payload.
  Test: `lint_plan.py --multi-tenant [plan]` fails when the isolation table lists no surface or the test plan has no
  cross-tenant entry (eval `output-multi-tenant-invoice-export`).
- [invariant] Facts in the plan are verified or labeled. Read or measure claims about the codebase, external APIs,
  limits and volumes. Label each decision-carrying claim verified, reported or inferred, as
  `evidence-before-claims` defines them. Read your own code before stating how it works.
  Why: a plan built on unchecked subagent reports contained many errors, including wrong statements about the
  project's own code.
  Test: every row of the Data model and Dependencies tables has an Evidence cell; review rejects a decision that
  rests on a claim not labeled verified.
- [invariant] Extend what exists; keep today's behaviour for existing data. Before adding a mechanism, find the
  existing one that solves the same kind of problem (resolver, policy, pipeline, component) and add the new axis
  there; name it in the Reuse section. A new field or default keeps today's behaviour for every existing data shape
  (records that never set it, records with explicit values, records using defaults) without a backfill, or the plan
  includes the backfill and its rollback. A default lives in one place.
  Why: parallel mechanisms drift. A default changed in the model but restated with the old value in a second code
  path hid a feature from every user, and a one-time backfill was undone by code paths that kept writing the old
  value.
  Test: the linter fails when the Reuse section is empty; the Data model table lists each existing data shape with
  its behaviour.
- [invariant] Rollout order and a concrete rollback. Order the rollout across components: receivers and control
  planes before senders and clients, schema before code (expand, migrate, contract), and risky or unfinished parts
  behind a flag that defaults to off. Describe how to roll back two hours after release, including the data written
  in between, and mark irreversible steps.
  Why: updated clients talking to an old receiver fail silently or flood it with errors, and a migration shipped
  after the code that needs it breaks the first request on the new path.
  Test: the linter fails when Rollout or Rollback is missing or empty.
  Source: parallel change (expand, migrate, contract), https://martinfowler.com/bliki/ParallelChange.html
  (verified 2026-10).
- [default] Steps with checkable done criteria. End the plan with an implementation table: step, location, a done
  criterion a reviewer can check, dependency. Done criteria come from the definition of done in `feature-delivery`.
  Trade-off: a longer plan; a very small plan may use a checklist and say so. Deviate only with an ADR that names
  this trade-off.
  Test: the linter checks the table header.
- [default] Adversarial self-review before handover. Answer the fixed questions in
  [references/self-review.md](references/self-review.md) in the plan's Self-review section. For critical plans
  (money, auth, tenant isolation, concurrency) get exactly one adversarial review from a reviewer that sees only the
  plan and the code.
  Trade-off: time and tokens before the owner sees anything. Deviate only with an ADR that names this trade-off.
  Test: the Self-review section answers every question with a fact or a number.
- [default] Search before creating. Search existing plans, issues, ADRs and decisions, including closed and
  cancelled ones, before writing a new plan. Don't reopen a topic that was explicitly cancelled; link to it.
  Trade-off: search time on every plan. Deviate only with an ADR that names this trade-off.
  Test: the Prior art section has links, or "none found in [where searched]".
- [default] Automation parity and read-after-write. What a user can do by clicking is also possible through the
  public API, and through the IaC provider if the product has one. Every writable field can be read back; secrets
  are write-only with a value that means "keep". API plan gating is part of the plan.
  Trade-off: more surface to build, test and document. Deviate only with an ADR that names this trade-off.
  Test: the API and automation section lists endpoints, error codes, pagination and the IaC resource, or N/A with a
  reason.
- [default] Performance budget in numbers. State expected volume (entities times frequency, rows per day, events
  per second), queries per request with a p95 target, analytical scan scope, queue load and payload sizes. Size
  lists for the large case, a hundred affected items rather than three, and say how lists are capped and totals
  shown.
  A view that reads many sources (a dashboard, a report) states per widget its source, cost and freshness; the
  loading and caching rules for such views are in `performance-gate`.
  Trade-off: estimates can be wrong; delivery replaces them with measurements. Deviate only with an ADR that names
  this trade-off.
  Test: every field in the Performance budget section holds a number or N/A with a reason.
- [default] Legal triggers. Answer yes or no for a new personal-data category, a new processor or sub-processor, a
  new retention period, a third-country transfer and special-category data. Hand any yes to `gdpr-engineering`.
  Trade-off: a legal check on features that turn out harmless. Deviate only with an ADR that names this trade-off.
  Test: the linter fails when one of the five triggers has no yes or no.
- [default] All UX states and destructive confirmations. Plan empty, loading, error, partial data, no permission
  and limit reached, plus mobile, keyboard and screen-reader behaviour, localisation, and confirmations for
  destructive actions that state the consequence. Reuse existing components and match the existing screen of the
  same type.
  Trade-off: more design work for small features. Deviate only with an ADR that names this trade-off.
  Test: the UX and states table has a line per state.

## Procedure

1. Search prior art: plans, issues, ADRs, closed and cancelled topics.
2. Frame the problem. If the request names a solution ("add a button"), use
   [references/problem-framing.md](references/problem-framing.md) first.
3. Read the code, schema and configuration the feature touches. Label each fact verified, reported or inferred.
4. Create the plan file from the project's template, or from
   [references/plan-template.md](references/plan-template.md) if the project has none. The path comes from the
   project facts file; the default is `docs/plans/YYYY-MM-DD-[slug].md`. Set `Status: Draft`, then `Tier:` and
   `Cost-intensive:` from the criteria in the template.
5. Fill every section. N/A with a reason; anything deferred becomes a linked issue.
6. Fill the failure-mode table and the open decisions.
7. Answer the self-review questions. For a critical plan, get one adversarial review and fold in what holds up.
8. Run the linter and fix every finding:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/lint_plan.py [plan]`, with `--multi-tenant` for a multi-tenant product and
   `--template [file]` when the project has its own template. In clients that don't set `CLAUDE_SKILL_DIR`, the
   script is in this skill's `scripts/` folder. Without Python, check the points listed at the end of the plan
   template by hand.
9. Gate: present the plan in the handover format below and stop. No code, no commit, no push. Present the
   decisions as text the owner can discuss, not as a forced multiple-choice prompt.
10. When the owner approves in the conversation, set `Status: Approved` and `Approved-by: [name], [date]`, record
    settled decisions as ADRs ([references/adr-template.md](references/adr-template.md)), and hand over to
    `feature-delivery`.

Handover format:

```text
Plan: docs/plans/2026-03-04-credit-notes.md (Status: Draft, Tier: full, not cost-intensive, linter passes)
Business goal: month-end corrections are the second most common support ticket; credit notes remove them.
Problem: accountants can't correct a sent invoice without cancelling it and losing the payment link.
Scope: credit notes for sent invoices, full and partial; no changes to tax calculation.
Biggest risk: a credit note posted twice on retry; covered by an idempotency key (failure modes, row 3).
Open decisions:
1. Allow partial credit notes in the first release? Recommendation: yes, because ...
2. Numbering: shared sequence with invoices or its own? Recommendation: its own, because ...
Nothing is implemented. Reply with approval, or answer by number ("1 yes, 2 own").
```

## Traps

- "Quick one", "just do it" or "no need for a plan" is not approval of a plan. Write a short plan and stop at the
  gate.
- A request phrased as a solution hides the problem. "Add an export button" may be "the auditor needs last
  quarter's invoices".
- A view designed for three items is unreadable when an event touches a hundred. Size for the large case.
- A default restated in a second code path keeps the old behaviour alive after the change.
- Lifecycle gaps: items that can be created but not edited, corrected, withdrawn or restored, or that duplicate on
  retry.
- Findings from subagents or earlier sessions copied into the plan without checking them.
- An option list without a recommendation, or a recommendation without the trade-off it accepts.
- Reopening a topic that was cancelled, instead of linking the earlier decision.
- A small UI on top of an expensive read: one new dashboard tile can be the most cost-intensive feature of the
  quarter. Classify by what runs per request, not by the size of the screen.
- Cost written as "low" or "negligible" without a number, or computed for today's tenants only.
- A business goal copied from the request ("users want X") instead of read from the brief or model.

## Done when

- The plan file exists at the project's plans path with `Status: Draft`, and the linter passes.
- The tier matches the stakes; a cost-intensive plan is `full` and its Cost model has numbers at today's size, 10x
  and 100x.
- Every section is answered, N/A has a reason, and every deferred item is a linked issue.
- Open decisions are numbered, each with options, trade-offs and a recommendation.
- The reply gives the plan path, the open decisions and a request for approval, and no code, commit or push
  happened.

## References

- [references/plan-template.md](references/plan-template.md): load when writing a plan and the project has no
  template of its own.
- [references/problem-framing.md](references/problem-framing.md): load when the request is phrased as a solution,
  or the personas and stress moment are unclear.
- [references/failure-modes.md](references/failure-modes.md): load when filling the failure-mode table.
- [references/self-review.md](references/self-review.md): load before handover.
- [references/open-decisions.md](references/open-decisions.md): load when writing the decision list.
- [references/adr-template.md](references/adr-template.md): load when a decision is settled and should be recorded.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding the plan gate to a project's
  CI, PR template or overlay.
- [scripts/lint_plan.py](scripts/lint_plan.py): run it on every plan before handover; `--help` lists its checks and
  `--self-test` runs its built-in fixtures.

## Sources

- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices: the plan-validate-execute
  pattern (create a plan file, validate it with a script, then execute); verified 2026-10.
- https://martinfowler.com/bliki/ParallelChange.html: expand, migrate, contract for backward-incompatible changes;
  verified 2026-10.
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions: ADR sections title, context, decision,
  status, consequences; verified 2026-10.
