# Changelog

All notable changes to the `core` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `evidence-before-claims`, `verify-before-done`, `safe-actions`, `feature-planning`, `feature-delivery` and `bug-investigation`.
- Skill `commit-hygiene` with a commit-msg hook, a CI range check and a pull request body check.
- Skills `project-inception`, `learning-loop`, `test-strategy`, `maintainable-code` and `agent-toolbelt`.
- Skills `stack-bootstrap` and `performance-gate`.
- Skills `goal-focus` and `agent-delegation`; `test-strategy` requires every new test to be seen failing and to assert outcomes.
- Skill `glossary`: about 230 verified terms from the EU and German software and business world, a project
  `docs/GLOSSARY.md` template and a format checker.
- `goal-focus` caps fix attempts on one failing check at ten, with a visible counter and a stop report.
- Skill `know-your-limits` for sessions on small or balanced models; `goal-focus` no longer cites a best-practices passage that was removed upstream.
- Skill `project-scaffold`: creates only the approved components from each stack's official starter (Laravel Vue
  kit, Nuxt, Go), with pinned versions, flags instead of prompts and an untouched first commit, plus
  `check_scaffold.py`.
- `stack-bootstrap` offers the `marketing` plugin, `web-quality-skills` and eight `marketingskills` skills for public marketing and docs sites.
- `evidence-before-claims` checks the status, authorship and security claims in README, specs and ADRs against
  CI runs, the ADR record and git history before a push, with `claim_scan.py` and a reference on rewriting them.
- `safe-actions` audits files and history for leaks before a repository or package goes public, with
  `leak_scan.py` (home paths, secrets, private terms, chat residue, internal hosts).
- `test-strategy` requires a failure proof in the real test environment for transport, transaction and timing
  behaviour, and an isolated clean state for end-to-end suites.
- `verify-before-done` selects CI runs by the pushed commit and requires a kill test for long-lived processes.
- `commit-hygiene` keeps a behaviour or design change and its test updates in one commit.
- `project-scaffold` audits starter leftovers against the approved specs, asks the owner per item and pins the
  allowed tables with a guard test.
- Skill `security-assurance`: every security property the product relies on or claims gets a row (property,
  asset, attacker, mechanism, evidence, not covered), each technique is checked for correct use (AEAD and
  nonces, keys, password hashing, CSPRNG tokens, constant-time compares, token algorithms, TLS verification),
  and each property has an attack test seen failing; `check_assurance.py` checks the table.
- `goal-focus`: autonomous work starts from the business goal, the feature goal and its criterion, and weighs each
  decision against UX, function, scale and cost, and security.
- `feature-planning`: plan depth follows the stakes (`Tier:` short, standard, full); a plan marked
  `Cost-intensive: yes` is full and carries a Cost model with cost per request and per tenant today, at 10x and
  100x, caching or precomputation, budget, overrun behaviour and the share of the price; the Problem section names
  the business goal; `lint_plan.py` checks both (P16, P17).
- `feature-delivery` replaces the Cost model's estimates with measurements before handover.
- `performance-gate`: data-heavy views load expensive widgets independently, cache them per tenant and permission
  scope with a freshness TTL, stale-while-revalidate and one refresh at a time, or precompute them; the gate
  measures them cold and warm and states the cost per view.
