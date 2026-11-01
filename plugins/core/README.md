# core

Working rules for coding agents that apply to every stack: check facts against a source before stating them,
call something done only after it was seen working, ask before actions that leave the machine, plan before
building, and investigate bugs from evidence instead of guesses.

The skills name tools by what they do, not by product. When a documentation index tool such as Context7 is
available they use it, and otherwise they fall back to the vendor's docs or mark a claim as unverified. The
optional [docs-tools](../docs-tools/README.md) plugin installs Context7.

## Skills

| Skill | Use it when |
|---|---|
| `evidence-before-claims` | an answer or a change depends on how a library, framework, API, CLI flag, config key or standard behaves in the installed version |
| `verify-before-done` | you are about to report something as done, fixed or working |
| `safe-actions` | an action has effects outside the working tree: push, deploy, migrate a shared database, send mail or SMS, touch payments, secrets or infrastructure |
| `feature-planning` | a feature needs a plan that an owner approves before code is written |
| `feature-delivery` | an approved plan is being built and has to end with evidence for each done item |
| `bug-investigation` | a defect has to go from report to a failing regression test and a root-cause fix |
| `project-inception` | a project starts or has no docs: product, business and architecture specs before code, a routing table for agents |
| `learning-loop` | you were corrected or hit a non-obvious trap and the lesson has to survive the session |
| `test-strategy` | deciding what to test, how deep, which tests gate a release, and what to do with flaky tests |
| `maintainable-code` | writing or reviewing code for reuse, seams, conventions and the cost of a new abstraction or dependency |
| `agent-toolbelt` | choosing the cheapest tool to answer a question, or briefing a subagent |
| `commit-hygiene` | you write commits, rewrite branch history or write a pull request description, or set up commit checks |

Claude Code loads a skill when the task matches its description. You can also call one directly, for example
`/core:evidence-before-claims`.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install core@rene-roscher-skills
```

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off). Project choices that are a matter of taste are not rules. They live in the example profile
under `templates/project-overlay/profiles/` at the repository root.

See [CHANGELOG.md](CHANGELOG.md) for changes.
