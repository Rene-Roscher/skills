# OIDC and secrets

## OIDC instead of stored keys

- The job that logs in to the cloud or signs keyless requests `id-token: write`. No other job does. Without that
  permission the job cannot request the OIDC token.
- OIDC credentials are short-lived and valid for one job. A stored cloud key is valid until someone rotates it.
- Use the cloud provider's official login action at a pinned SHA, with the role or identity to assume. Don't store
  the role's long-lived key as a fallback.

## Trust-policy conditions

The cloud side decides which GitHub tokens it accepts. GitHub's OIDC reference requires at least one condition so
that untrusted repositories cannot request access tokens. Write the narrowest one the job allows:

| Job | `sub` condition |
|---|---|
| deploy to production through an environment | `repo:OWNER/REPO:environment:production` |
| release from a tag | `repo:OWNER/REPO:ref:refs/tags/v*` (if the provider supports wildcards there) |
| main-branch publish | `repo:OWNER/REPO:ref:refs/heads/main` |

- Never a condition on the owner alone (`repo:OWNER/*`). Every repository in the organization, including new
  ones, could then assume the role.
- Check `aud` as well, set to the value your provider documents.
- Keep the trust policy in infrastructure code with a test that asserts the `sub` condition names the repository
  and an environment or ref.
- Check the claim format and wildcard support in your cloud provider's GitHub OIDC guide before writing it; the
  table shows GitHub's subject format, not every provider's matching rules.

## Registries and package publishing

- GHCR and GitHub Packages: `GITHUB_TOKEN` with `packages: write` on the publishing job.
- Cloud registries: OIDC.
- Package registries that offer trusted publishing (OIDC-based, no stored token): use it. zizmor
  `use-trusted-publishing` reports packaging workflows that could.

## Environments

- Production deploy secrets live in an environment, not at repository level.
- The environment has required reviewers and deployment branch or tag rules. All deployment protection rules must
  pass before a job that references the environment is sent to a runner.
- zizmor `secrets-outside-env` (auditor persona) reports secrets used in jobs without an environment.

## Secret hygiene

- Forward named secrets to reusable workflows. `secrets: inherit` passes every secret the caller can see.
- Don't store structured secrets (JSON, YAML). Log redaction matches the whole value, so a single field printed
  on its own is not masked. zizmor `unredacted-secrets` looks for this.
- `actions/checkout` with `persist-credentials: false` unless the job pushes with git. Otherwise the token stays
  in `.git/config` for every later step and any uploaded artifact that includes the directory.

## Sources

- https://docs.github.com/en/actions/concepts/security/openid-connect (verified 2026-10)
- https://docs.github.com/en/actions/reference/security/oidc (verified 2026-10)
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax (verified 2026-10)
- https://docs.zizmor.sh/audits/ (verified 2026-10)
