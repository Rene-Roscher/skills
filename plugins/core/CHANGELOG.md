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
- `stack-bootstrap` offers the `marketing` plugin, `web-quality-skills` and eight `marketingskills` skills for public marketing and docs sites.
