# Permissions and tokens

## The block

- `permissions: {}` at workflow level disables every scope. As soon as any scope is set, every scope not listed is
  `none`.
- Allowed forms: `read-all`, `write-all`, `{}`, or a map of scopes with `read`, `write` or `none`. Some scopes
  accept only a subset (for example `vulnerability-alerts: read|none`). There is no `minimal` or similar keyword.
- Grant per job. A job's `permissions:` replaces the workflow-level block for that job; it does not add to it.
- Every grant gets a comment saying why. zizmor `undocumented-permissions` asks for that.

## Which job needs which scope

| Job does | Scope |
|---|---|
| checks out the repository | `contents: read` |
| pushes commits, tags or creates a release | `contents: write` |
| pushes to GitHub Packages or GHCR | `packages: write` |
| exchanges an OIDC token (cloud login, keyless signing) | `id-token: write` |
| creates an artifact attestation | `attestations: write` plus `id-token: write` |
| comments on a pull request | `pull-requests: write` |
| uploads SARIF to code scanning | `security-events: write` |
| creates a deployment | `deployments: write` |

Check the scope list in the workflow syntax reference before adding one that is not in this table.

## Pull-request triggers

- Pull requests from forks get a read-only token and no secrets.
- Pull requests from branches in the same repository get the scopes the workflow grants. A write scope or
  `id-token: write` at workflow level in a `pull_request` workflow reaches every job that runs for such a branch.
  Keep write scopes on jobs that don't run for pull requests (`if:` on the event), or in a separate workflow.

## Choosing the token

- `GITHUB_TOKEN`: the default. Scoped to the repository, expires with the job.
- Events created with `GITHUB_TOKEN` don't start new workflow runs, except `workflow_dispatch` and
  `repository_dispatch`, and pull requests it opens or updates wait for approval. When a workflow must trigger
  another, use a GitHub App installation token minted per run with the narrowest repository and permission set.
- Personal access tokens: avoid. They are long-lived, bound to a person, and usually broader than the job needs.
  A PAT in `docker/login-action` or a release step is a finding.

## Repository default

Set the repository or organization default for `GITHUB_TOKEN` to read-only. A workflow without a `permissions`
block otherwise inherits the default, which is permissive on older accounts.

## Sources

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax (verified 2026-10)
- https://docs.github.com/en/actions/concepts/security/github_token (verified 2026-10)
- https://docs.github.com/en/actions/reference/security/secure-use (verified 2026-10)
