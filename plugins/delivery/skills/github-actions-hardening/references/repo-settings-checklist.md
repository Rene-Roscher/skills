# Repository and organization settings

The workflow files only hold if the settings back them. The agent reads settings and reports differences; an
administrator changes them. Any write call (`gh api -X PUT`, `-X PATCH`, `-X POST`) is an action with effects
outside the working tree and needs approval first (`safe-actions`).

## Checklist

| Setting | Target |
|---|---|
| Default `GITHUB_TOKEN` permissions | read-only |
| Workflows may approve pull request reviews | off |
| Allowed actions | GitHub-owned and an allowlist, or verified creators plus an allowlist |
| Pinning policy | "Require actions to be pinned to a full-length commit SHA", or "Require lockfile" when adopted |
| Actions event policy (public repositories) | decided: keep the default rule that disables `pull_request_target`, or allow it for named workflow files |
| Fork pull request workflows | approval required for outside contributors |
| Runner groups | release runners in their own group, restricted to selected repositories |
| Branch ruleset on the default branch | required checks include the gate jobs and the workflow lint; code-owner review |
| Tag ruleset | protects `v*` against creation, update and deletion by anyone but the release path |
| Environments | production has required reviewers and deployment branch or tag rules |
| CODEOWNERS | covers `/.github/` |

## Read-only audit

```bash
set -eu
repo="OWNER/REPO"
gh api "repos/$repo/actions/permissions"
gh api "repos/$repo/actions/permissions/workflow"
gh api "repos/$repo/actions/permissions/selected-actions" || true # 404 when all actions are allowed
gh api "repos/$repo/rulesets" --paginate
gh api "repos/$repo/environments" --paginate
gh api "repos/$repo/contents/.github/CODEOWNERS" --jq .path || echo "no .github/CODEOWNERS"
```

The `|| true` here is not a gate: the audit prints a report, and a missing endpoint is part of the report.

For organizations, add the organization-level equivalents (`orgs/ORG/actions/permissions`,
`orgs/ORG/actions/runner-groups`). Field names change over time; read them from the response instead of hard-coding
a schema, and compare against the checklist by hand or with a small script that prints differences.

Output: a table of setting, current value, target, and who can change it. Nothing else.

## Sources

- https://docs.github.com/en/actions/reference/security/secure-use (verified 2026-10)
- https://docs.github.com/en/actions/how-tos/administer/enforce-workflow-lockfiles (verified 2026-10)
- https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available/ (verified 2026-10)
- https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access (verified 2026-10)
