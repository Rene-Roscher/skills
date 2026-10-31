# Lint gates: zizmor and actionlint

## zizmor

- Pin the version, both in CI and in local instructions. Install from a release artifact with a checksum, from a
  pinned package version, or through `zizmorcore/zizmor-action` at a SHA with an explicit version input.
- Personas: `regular` (default), `pedantic`, `auditor`. Some audits only report under `pedantic` or `auditor`, for
  example `self-hosted-runner`, `concurrency-limits` and `secrets-outside-env`. Run `regular` as the blocking gate
  and `auditor` during reviews.
- Filters: `--min-severity` and `--min-confidence`.
- Exit codes: `0` no findings, `1` audit error, `2` argument error, `3` no inputs collected, `11` to `14` findings
  whose highest severity is informational, low, medium or high.
- With `--format=sarif` zizmor does not use exit codes 11 and above. A job that only uploads SARIF passes with
  findings. Either run a second, blocking step with `--format=plain` or `--format=github`, or make the code
  scanning result a required check.
- SARIF upload needs `security-events: write` on that job only.
- Inline suppression: `# zizmor: ignore[rule-name]`, several rules separated by commas, with a trailing
  explanation. A suppression without a reason is a review finding.
- Configuration in `.github/zizmor.yml` or `zizmor.yml`. No blanket disables. Keep `unpinned-uses` at its default
  policy, which since v1.20.0 requires hash pins for every action.

## actionlint

- Checks workflow syntax, expression types, `needs:` references, runner labels and more, and integrates
  shellcheck for `run:` scripts when shellcheck is installed.
- Pin its version the same way. Install shellcheck at a pinned version too, and fail the job if `shellcheck` is
  missing: actionlint v1.7.12 given `-shellcheck=no-such-command` and a `run: echo $FOO` step exits 0 without a
  message (reproduced 2026-10-31), so a runner without shellcheck skips the `run:` checks unnoticed.

## Wiring

- Separate jobs for actionlint, zizmor and the workflow checker, so one red job doesn't hide the others.
- Trigger on pull requests that touch `.github/**`, `**/action.yml` or `**/action.yaml`, and on pushes to the
  default branch.
- `permissions: {}` at workflow level; `contents: read` per job; `security-events: write` only on a SARIF upload
  job.
- Make the lint jobs required checks in the branch ruleset.

## Proving the gate

Keep a seeded-bad workflow under a fixtures directory that is not in `.github/workflows/`, with one known finding
per audit you depend on (an unpinned `uses:`, a `${{ github.event.pull_request.title }}` in `run:`, a workflow
without `permissions`). A self-test step runs the tools on the fixture and fails if they report nothing.

## Sources

- https://docs.zizmor.sh/usage/ (verified 2026-10)
- https://docs.zizmor.sh/audits/ (verified 2026-10)
- https://docs.zizmor.sh/integrations/ (verified 2026-10)
- https://github.com/rhysd/actionlint (verified 2026-10)
