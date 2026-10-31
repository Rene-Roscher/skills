---
type: llm
weight: 3
focus:
  source: file
  path: .github/workflows/release.yml
---

Judge the file `.github/workflows/release.yml`.

PASS if all of these hold: the top-level `permissions` is `{}` or only `contents: read`; `packages: write`, `id-token: write` or other write scopes appear only on the job that pushes or deploys; the push or deploy job has a `needs:` chain to a job that runs the tests in the same run (for example a job that calls `ci.yml` through `workflow_call`, or a test job inside release.yml); every job sets `timeout-minutes`; every `uses:` is either a full 40-character commit SHA with a version comment or an explicit placeholder marked for resolution from the action's own repository; values such as the tag name reach `run:` only through `env:`.
FAIL if any of these is missing.
