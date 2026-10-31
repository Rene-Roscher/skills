# Sign, attest, verify

Signing is only worth something if a gate verifies it before the image runs. Plan both ends together. The CI job's
permissions, trigger and runner follow `github-actions-hardening`.

## Release job order

1. Build the production target and run the smoke test and the scan on it.
2. Push by digest, without tags (build-push-action `outputs: type=image,push-by-digest=true,name-canonical=true,push=true`),
   and read the digest from the step output.
3. Sign the digest keyless: `cosign sign --yes [registry]/[image]@[digest]`. Never sign a tag.
4. Attest. Provenance and SBOM from the build step (build-push-action `provenance` and `sbom` inputs) and/or
   GitHub artifact attestations with `actions/attest` (`actions/attest-build-provenance` is a wrapper around it
   since v4, and its README says new implementations should use `actions/attest`).
5. Create the tags on the signed digest (`docker buildx imagetools create`).
6. Verify in the same job, with the same identity the deployment will check:

```bash
cosign verify "[registry]/[image]@[digest]" \
  --certificate-identity-regexp '^https://github\.com/OWNER/REPO/\.github/workflows/release\.yml@refs/tags/v' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com'
gh attestation verify "oci://[registry]/[image]@[digest]" -R OWNER/REPO
```

Anchor the identity regexp at both the repository and the workflow file, and include the ref prefix. A regexp such
as `OWNER/REPO` alone accepts every workflow and every branch in the repository.

Permissions the release job needs: `id-token: write` (keyless signing and attestations), `packages: write` (push
to GHCR), `attestations: write` (GitHub attestations). Nothing else.

## Deployment-side verification

- The gate checks repository, workflow file, ref and issuer, not only "has a signature".
- Admission policy (preferred): Kyverno `ImageValidatingPolicy` with a keyless attestor (subject and issuer, or
  their regexp forms), plus digest verification or mutation so the pod runs the verified digest. Sigstore's
  policy-controller is an alternative.
- Without an admission controller: verify in the GitOps tool if it supports it, or in the deploy script with the
  same `cosign verify` command, before the manifest is applied.
- Deploy manifests reference digests (`image: [registry]/[image]@sha256:[digest]`), or tags resolved and verified
  to digests by the policy.
- Policy test in the deployment repository (for Kyverno, `kyverno test`): one unsigned image and one image signed
  by a different workflow or ref must be rejected; the release image must pass.

## Traps

- Signing `:latest` signs whatever the tag pointed to at that moment, and the signature stays attached while the
  tag moves.
- A release re-run through `workflow_dispatch` signs under a branch ref. The anchored verifier rejects it, which
  is correct. Re-tag instead of widening the regexp.
- Verifying only in CI proves the release job, not what the cluster runs.

## Sources

- https://github.com/sigstore/cosign/blob/v3.1.4/README.md (sign by digest) (verified 2026-10)
- https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify.md (verified 2026-10)
- https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations (verified 2026-10)
- https://github.com/actions/attest-build-provenance (verified 2026-10)
- https://kyverno.io/docs/policy-types/image-validating-policy/ (verified 2026-10)
- https://github.com/docker/build-push-action (verified 2026-10)
