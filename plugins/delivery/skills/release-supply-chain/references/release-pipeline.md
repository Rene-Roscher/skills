# Release pipeline

## Contents
- Step order
- Release job sketch
- Checksum chain check
- Release notes block
- Downloaded tools

Check every command against the installed tool version (`cosign version`, `syft version`, `gh --version`).
Permissions, pinning and runner rules come from `github-actions-hardening`.

## Step order

| # | Step | Fails the release when |
|---|---|---|
| 1 | Preflight: gates green on this commit, tag signed by an allowed signer, signing identity or key available | any check fails |
| 2 | Build every target once, reproducible settings | build or double-build mismatch |
| 3 | SBOM per artifact into `dist/` | count of SBOMs differs from count of artifacts |
| 4 | Copy the verifier script into `dist/` | missing |
| 5 | `SHA256SUMS` over everything in `dist/`, generated last | asset list and checksum list differ |
| 6 | Sign `SHA256SUMS` | signing fails |
| 7 | Verify the signature in the same job with identity and issuer | verify fails |
| 8 | Provenance and SBOM attestations | attestation fails |
| 9 | Publish the release with the verify block first | body check fails |
| 10 | Images: push by digest, sign, attest, tag, re-verify (`container-images`) | any step fails |

## Release job sketch

```yaml
on:
  push:
    tags: ['v*']
permissions: {}
jobs:
  release:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    permissions:
      contents: write
      id-token: write
      attestations: write
      artifact-metadata: write
    steps:
      # checkout, toolchain and tool installs pinned by SHA and checksum
      - name: Build
        run: make release-build            # writes dist/[name]_[os]_[arch]
      - name: SBOM per artifact
        shell: bash
        run: |
          shopt -s nullglob
          bins=(dist/agent_*)
          test "${#bins[@]}" -eq "$EXPECTED_ARTIFACTS"
          for b in "${bins[@]}"; do syft "file:$b" -o "cyclonedx-json=$b.cdx.json"; done
      - name: Checksums
        shell: bash
        run: |
          cd dist
          LC_ALL=C find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%f\n' | LC_ALL=C sort \
            | xargs sha256sum > SHA256SUMS
      - name: Sign and verify
        shell: bash
        run: |
          cosign sign-blob dist/SHA256SUMS --bundle dist/SHA256SUMS.sigstore.json --yes
          cosign verify-blob dist/SHA256SUMS --bundle dist/SHA256SUMS.sigstore.json \
            --certificate-identity "https://github.com/${GITHUB_REPOSITORY}/.github/workflows/release.yml@${GITHUB_REF}" \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com
      - uses: actions/attest@[sha] # v4
        with:
          subject-checksums: dist/SHA256SUMS
```

Notes:
- `GITHUB_REF` on a tag push is `refs/tags/vX.Y.Z`, so the identity is exact for this release.
- The bundle file is published next to `SHA256SUMS`. It is not listed inside it, because it is created after.
- Check the `actions/attest` inputs for the version you pin; `subject-path`, `subject-digest` and
  `subject-checksums` are mutually exclusive.

## Checksum chain check

```bash
set -euo pipefail
cd dist
diff <(LC_ALL=C find . -maxdepth 1 -type f ! -name 'SHA256SUMS*' -printf '%f\n' | LC_ALL=C sort) \
     <(awk '{print $2}' SHA256SUMS | sed 's#^\*##' | LC_ALL=C sort)
sha256sum -c SHA256SUMS
```

## Release notes block

The body starts with this block, filled in by the release job:

````markdown
## Verify this release

```bash
cosign verify-blob SHA256SUMS --bundle SHA256SUMS.sigstore.json \
  --certificate-identity https://github.com/[org]/[repo]/.github/workflows/release.yml@refs/tags/vX.Y.Z \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
sha256sum --ignore-missing -c SHA256SUMS
gh attestation verify [artifact] -R [org]/[repo]
```
````

For key-signed releases, replace the identity flags with `--key [public key URL pinned in the docs]`.

## Downloaded tools

```bash
set -euo pipefail
VERSION=X.Y.Z
SHA256=[64 hex characters recorded with the version]
curl -fsSLo tool.tar.gz "https://github.com/[vendor]/[tool]/releases/download/v${VERSION}/[tool]_${VERSION}_linux_amd64.tar.gz"
echo "${SHA256}  tool.tar.gz" | sha256sum -c -
tar -xzf tool.tar.gz [tool]
```

Where the vendor signs releases, verify that signature with the vendor's documented identity as well. A
SHA-pinned setup action with an explicit tool version is the alternative.
