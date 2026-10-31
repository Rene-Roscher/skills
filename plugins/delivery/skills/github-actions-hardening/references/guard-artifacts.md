# Guard artifacts

## Contents

- Files to create in the target repository
- The workflow checker
- Seeded-bad fixtures and the self-test
- Updater and CODEOWNERS entries

These files make the rules hold by build instead of by agent compliance. Create them in the target repository,
adapted to its layout. Placeholders in square brackets are filled from the repository; SHAs are resolved as in the
pinning procedure, never copied from here.

## Files to create in the target repository

| File | Purpose |
|---|---|
| `.github/workflows/workflow-lint.yml` | actionlint, zizmor and the workflow checker as separate blocking jobs |
| `.github/zizmor.yml` | zizmor configuration: no blanket disables, every override with a reason |
| `scripts/ci/check-workflows` (or the project's script location) | the checks zizmor and actionlint don't do |
| `scripts/ci/fixtures/bad-workflow.yml` | a workflow that breaks every checked rule once |
| `.github/dependabot.yml` or a Renovate config | updater for the actions ecosystem with grouping and cooldown |
| `.github/CODEOWNERS` | an entry for `/.github/` |
| `scripts/ci/audit-repo-settings` | read-only settings audit (commands in the settings checklist reference) |

If the lockfile is adopted, add `gh actions-lock --verify` as a required check.

Skeleton for the lint workflow. Every `uses:` gets a resolved SHA and its version comment:

```yaml
name: workflow-lint
on:
  pull_request:
    paths: [".github/**", "**/action.yml", "**/action.yaml", "scripts/ci/**"]
  push:
    branches: [main]
permissions: {}
concurrency:
  group: workflow-lint-${{ github.ref }}
  cancel-in-progress: true
jobs:
  actionlint:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read # checkout
    steps:
      - uses: actions/checkout@[sha] # v[x.y.z]
        with:
          persist-credentials: false
      - name: actionlint
        shell: bash
        run: |
          # install actionlint and shellcheck at pinned versions, verified with sha256sum -c
          command -v shellcheck >/dev/null || { echo "::error::shellcheck missing"; exit 1; }
          actionlint
  zizmor:
    # same shape; run zizmor with --format=github so findings fail the job
  check-workflows:
    # same shape; run the checker on .github/workflows, then its self-test on the fixture
```

## The workflow checker

Write it in the language the repository already uses for tooling, with a real YAML parser (a YAML library already
in the dev dependencies, or `yq`). Grep alone misreads multi-line `run:` blocks and nested keys.

Checks, each with a message that names the rule and the fix:

1. A top-level `permissions` key exists.
2. No top-level write scope when `pull_request` is a trigger.
3. Every job has `timeout-minutes`.
4. Every job with a write scope, `id-token: write` or `environment:` transitively `needs` a job from the gate list.
5. Workflows triggered by tags, or with an `environment:`, use `cancel-in-progress: false` and `queue: max`.
6. No `|| true`, `set +e` or `continue-on-error: true` unless the line carries `# allow: [reason]`.
7. No `@latest`, no `version: latest`, no download piped into a shell.
8. No `${{` inside `run:` except an allowlist (`runner.temp`, `runner.os`, `github.run_id`, `github.workspace`).
9. Jobs with `id-token: write` or write scopes use a runner label from the release allowlist, never an expression.
10. No `workflow_dispatch` in a workflow that both requests `id-token: write` and signs.
11. A `pull_request_target`, `workflow_run` or `issue_comment` workflow that checks out a pull-request ref runs no
    step outside an allowlist.
12. Multi-line `run:` blocks in bash jobs set `shell: bash` (directly or through `defaults.run.shell`).

Keep the gate list and the runner allowlist in one configuration file that the checker and the documentation
both read.

## Seeded-bad fixtures and the self-test

- `bad-workflow.yml` violates each check exactly once, with a comment naming the check.
- The self-test runs the checker on the fixture and asserts a non-zero exit and one finding per check. A checker
  that reports nothing on the fixture fails the job.
- Keep the fixture outside `.github/workflows/`, so GitHub never runs it and zizmor's repository scan doesn't
  report it. Run zizmor and actionlint on it explicitly in the self-test to prove those gates as well.

## Updater and CODEOWNERS entries

Updater, minimal shape for Dependabot:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      actions:
        patterns: ["*"]
    cooldown:
      default-days: 7
```

Renovate: extend `helpers:pinGitHubActionDigests` and set a minimum release age for the actions manager.

CODEOWNERS:

```text
/.github/ @[team-or-owner]
```

Then a branch ruleset that requires code-owner review, and a tag ruleset that protects `v*`.

## Sources

- https://docs.zizmor.sh/usage/ (verified 2026-10)
- https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference (verified 2026-10)
- https://docs.github.com/en/actions/reference/security/secure-use (verified 2026-10)
