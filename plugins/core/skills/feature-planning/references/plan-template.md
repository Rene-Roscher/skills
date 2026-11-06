# Plan template

## Contents

- How to use it
- The template
- What the linter expects

## How to use it

Copy the block below into the project's plans folder (default `docs/plans/YYYY-MM-DD-[slug].md`) and replace
every bracketed placeholder. Keep the section headings: the linter finds sections by name, not by number. A
section marked "(optional)" may be deleted; the Cost model section is required when the header says
`Cost-intensive: yes` and may be deleted otherwise.

Set the tier before writing (the rule is in SKILL.md):

- `short`: reversible, no new stored data, no new cost, no change to money, auth or tenancy (a label, a layout, a
  filter over data already loaded). One line per section; N/A with its reason where it does not apply.
- `standard`: new stored data, endpoints, jobs or integrations without notable running cost.
- `full`: cost-intensive, money, authentication, tenant isolation, irreversible data changes, or a feature the
  business model depends on. Numbers measured on representative data where an estimate would decide, alternatives
  compared by cost, one adversarial review.

`Cost-intensive: yes` when the feature fans out to many sources or recipients, aggregates large data per request,
calls paid APIs or sends paid messages, stores large volumes, or computes per request in a way that grows with
tenant size. A cost-intensive plan is always `full`.

Every section gets an answer. "N/A" is allowed with a reason specific to this feature, on the same line. Deferred
work becomes a tracked issue with a priority, linked on the line that defers it. Label facts in the Evidence
columns as verified (with file:line, a command and its output, or a URL), reported (someone said so, not checked)
or inferred (concluded from other facts).

## The template

```markdown
# Plan: [feature name]

Status: Draft
Approved-by:
Date: [YYYY-MM-DD]
Issue: [link, or none]
Multi-tenant: [yes or no]
Tier: [short, standard or full]
Cost-intensive: [yes or no]

## 1. Problem
- Problem: [the problem, with no solution in it]
- Business goal: [why the project needs it: revenue, retention, cost, an obligation; from the brief or model]
- Personas: [who has it; each expects something different]
- Today: [what they do instead today]
- Success moment: [the moment they notice it works, from their view]
- Success metric: [a number and how it is measured]
- Non-goals: [what this plan does not do]
- Stress moment: [the moment of highest stress in which the feature is used]

## 2. Prior art
[plans, issues, ADRs and decisions found, including closed and cancelled ones, or "none found in [where searched]"]

## 3. Market comparison (optional)
[how comparable products solve it, and what this plan does differently]

## 4. UX and states
| State | What the user sees |
|---|---|
| Empty | [ ] |
| Loading | [ ] |
| Error | [ ] |
| Partial data | [ ] |
| No permission | [ ] |
| Limit reached | [ ] |

- Large case: [what the screen shows with 100 or more items, how lists are capped and totals shown]
- Mobile, keyboard and screen reader: [ ]
- Localisation: [ ]
- Destructive actions and their confirmation text: [ ]
- Existing components reused: [ ]

## 5. Data model
| Change | Existing data shapes and the behaviour for each | Index and the query it serves | Evidence |
|---|---|---|---|
| [new column, table or default] | [never set / explicit value / default: behaviour] | [index: query] | [verified: file:line] |

- Backfill and its rollback: [or N/A with the reason]

## 6. Reuse
- Existing mechanism extended: [resolver, policy, pipeline or component, with its path]
- Where the default lives: [the one place]

## 7. API and automation
- Endpoints: [method, path, request, response]
- Error codes: [ ]
- Pagination and filters: [ ]
- IaC resource: [or N/A with the reason]
- Read-after-write: [every writable field can be read back; secrets write-only with a keep value]
- Plan gating: [which plans get it]

## 8. Events, jobs and caching
- Events and realtime channels: [ ]
- Jobs and queues: [which queue, idempotency key, retries]
- Cache keys and invalidation: [key, tags, what invalidates it]

## 9. Permissions, limits and audit
- Permissions: [names and who has them]
- Limits: [plan limits and what happens at the limit]
- Audit entries: [what is logged, without personal data in the message]

## 10. Tenant isolation
| Surface | How tenant A is kept out of tenant B's data |
|---|---|
| [UI, API, export, webhook, public page, realtime channel, cache key, search, job, admin view] | [ ] |

## 11. Data protection
- New personal-data category: [yes or no]
- New processor or sub-processor: [yes or no]
- New retention period: [yes or no]
- Third-country transfer: [yes or no]
- Special-category data: [yes or no]
- Handed to: [gdpr-engineering, or N/A with the reason]

## 12. Dependencies
| Dependency | What the plan relies on | Evidence |
|---|---|---|
| [library, service or API] | [version, limit or behaviour] | [verified: URL or file:line] |

## 13. Performance budget
- Volume: [entities times frequency, rows per day, events per second]
- Queries per request and p95 target: [ ]
- Analytical or search scan scope: [ ]
- Queue load: [jobs per minute at peak]
- Payload sizes: [ ]

## 14. Cost model (required when Cost-intensive: yes)
- Cost drivers: [queries and scans, paid API calls, messages, storage, compute per request]
- Per request or action: [number with unit: queries, database time, calls, messages]
- Per tenant per month today: [number with unit, for the largest tenant]
- At 10x: [number with unit]
- At 100x: [number with unit]
- Cached or precomputed: [which reads, key scope, TTL from the freshness the user needs, rollups]
- Budget: [ceiling per request and per tenant per month]
- When exceeded: [limit, plan entitlement, degraded mode, kill switch]
- Against the price: [cost as a share of what the tenant pays]

## 15. Failure modes
| Failure | Impact | Detection | Reaction |
|---|---|---|---|
| [a dependency is down] | [ ] | [ ] | [ ] |
| [partial data] | [ ] | [ ] | [ ] |
| [retry creates a duplicate] | [ ] | [ ] | [ ] |

- Irreversible: [ ]
- Costs money or reaches people if it fires wrongly: [ ]

## 16. Test plan
- Unit and feature tests: [ ]
- Cross-tenant test per new resource: [or N/A for a single-tenant product, with the reason]
- Failure-mode tests: [ ]
- Browser check: [ ]

## 17. Rollout and rollback
- Rollout: [order across components, schema before code, flag default]
- Rollback: [how to roll back two hours after release, including data written since]
- Irreversible steps: [ ]

## 18. Implementation steps
| Step | Location | Done criterion | Depends on |
|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] |

## 19. Self-review
[answers to the self-review questions, with numbers]

## 20. Open decisions
1. [Question]
   - Options: [A], [B]
   - Trade-offs: [cost, reversibility, effort, risk]
   - Recommendation: [option], because [reason]
```

## What the linter expects

`scripts/lint_plan.py` checks a plan written from this template. It reports `path:line: code message` and exits 1
when it finds anything.

- A `Status:` line with Draft, Approved or Superseded; `Approved-by:` filled when the status is Approved.
- Every section above except the optional one, none of them empty, no bracketed placeholder left.
- No bare N/A: at least three words of reason on the same line or in the same table cell.
- No TBD, TODO or FIXME, and no answer that is only "later" or "follow-up", without an issue link on the same line.
- `Tier:` short, standard or full, and `Cost-intensive:` yes or no in the header.
- The eight Problem fields, each with a value.
- Evidence cells of verified, reported or inferred in the Data model and Dependencies tables.
- The five Data protection triggers answered yes or no.
- The failure-mode table header and at least three rows.
- Rollout and Rollback filled.
- The implementation table header and at least one row.
- Open decisions as a numbered list, each item with `Recommendation:`, or "None" with a reason.
- With `Cost-intensive: yes`: `Tier: full`, and the Cost model section with all nine fields; the per-request,
  per-tenant, 10x, 100x, budget and price fields each hold a number.
- With `--multi-tenant` or `Multi-tenant: yes`: at least one surface in the isolation table and a cross-tenant entry
  in the test plan.
