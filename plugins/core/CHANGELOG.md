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
