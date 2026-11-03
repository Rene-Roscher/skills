---
name: release-supply-chain
description: "Release rules for binaries, packages and images: immutable semver tags, build once and promote by digest, cosign keyless in CI versus an offline key for self-updaters, SBOM and provenance, verify before run, signed checksums, no @latest or install-by-pipe, self-update with rollback, ring rollouts. Use when cutting, signing or rolling out a release. Not for workflow permissions or Dockerfiles."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Release supply chain

This skill decides what a release is, how it is signed and described, who verifies it, and how it reaches a fleet.
Workflow mechanics (permissions, action pinning, OIDC trust, gates on the same commit) belong to
`github-actions-hardening`; image builds, image signing order and admission policies to `container-images`; wire
compatibility between the versions in a fleet to `cross-service-contracts`. Cosign, syft and GitHub attestation
syntax stays in their docs. The failure it prevents: a release whose signature nobody checks, an artifact in
production that was rebuilt after testing, and an agent fleet that installs whatever its download origin serves.

## Applies when / does not apply

- Applies: tagging a release, a release workflow that builds binaries, packages or images, signing and verifying
  artifacts, SBOM and provenance, checksum files, install scripts and download instructions, self-updating agents
  or CLIs, promoting an artifact between environments, rolling a version out to a fleet, writing release notes.
- Does not apply: job permissions, triggers and runners (`github-actions-hardening`); Dockerfile contents, base
  images and the image-specific sign-then-tag order (`container-images`); message compatibility between versions
  (`cross-service-contracts`); app deploys that are only a GitOps image bump (`container-images` covers the image).

## Rules

Ordered by blast radius. Examples use a server agent that customers install and that updates itself, plus a
control-plane image.

### What a release is

- [invariant] A published version never changes: a tag, the artifacts attached to it and the image digest it names
  stay fixed, and a fix is a new version. Release tags follow `vMAJOR.MINOR.PATCH`, prereleases carry a suffix
  (`-rc.1`) and never become `latest` or a stable channel. A tag ruleset forbids updating and deleting `v*` tags.
  Why: a moved tag makes every signature, checksum and pinned deployment of that version refer to different bytes.
  Test: pushing a changed `v1.4.0` is rejected by the ruleset; a prerelease run leaves the stable channel and
  `latest` untouched. Source: SemVer item 3, "Once a versioned package has been released, the contents of that
  version MUST NOT be modified." (https://semver.org/, verified 2026-11).
- [default] Release tags are signed (`git tag -s`, with SSH or OpenPGP selected by `gpg.format`), and the release
  workflow's preflight verifies the tag against an allowed-signers list before building. Trade-off: every
  maintainer needs a signing key, and the allowed-signers file is one more thing to maintain. Deviate only with an
  ADR that names this trade-off. Test: an unsigned tag pushed to a test repository fails the preflight before any
  build step. Source: `git tag -s` "Make a cryptographically signed tag"; `-v` verifies
  (https://git-scm.com/docs/git-tag, verified 2026-11).
- [invariant] Build once, promote by digest. The artifact that reaches production has the same digest as the one
  that passed staging; promotion moves a pointer (a tag, a manifest entry, a rollout record), it never rebuilds.
  Deploy references and rollout records carry `sha256` digests. Why: a rebuild for production is an artifact
  nobody tested, and the signature on the tested one does not cover it. Test: the production manifest's digest
  equals the digest the staging deploy recorded; a CI check rejects image references without `@sha256:`. Source:
  cosign "Always sign images based on their digest (@sha256:...) rather than a tag"
  (https://github.com/sigstore/cosign/blob/v3.1.4/README.md, verified 2026-11).

### Signing and verification

- [default] CI artifacts are signed keyless with cosign through the CI provider's OIDC token: binaries through a
  signed `SHA256SUMS` (`cosign sign-blob SHA256SUMS --bundle SHA256SUMS.sigstore.json --yes`), images by digest.
  The same job verifies with an exact `--certificate-identity` (or a regexp anchored on both ends to the release
  workflow and `refs/tags/v`) and `--certificate-oidc-issuer https://token.actions.githubusercontent.com`.
  Trade-off: the signer identity is a workflow, not a person; public repositories write the identity to a public
  transparency log; trust rests on Sigstore's infrastructure. Deviate only with an ADR that names this trade-off.
  Source: `cosign sign-blob artifact --bundle artifact.sigstore.json --yes` and `verify-blob` with identity and
  issuer (https://github.com/sigstore/cosign/blob/v3.1.4/README.md, verified 2026-11).
- [invariant] A self-updater's trust anchor never comes from the channel that delivers the artifact. It is a public
  key compiled into the binary, or a pinned identity plus trust root shipped with the binary, and the updater
  verifies the signature over the artifact digest before anything is replaced. A checksum served next to the
  artifact is integrity, not authenticity. Why: whoever controls the download origin controls both the bytes and
  the checksum file. Test: serve a modified binary with a matching checksum from a test origin; the updater
  refuses, keeps the running binary and reports the refusal. Source: TUF goal against arbitrary installation, "An
  attacker cannot install anything they want on the client system"
  (https://theupdateframework.github.io/specification/latest/, verified 2026-11).
- [default] Self-updating fleets use an offline signing key: the private key lives on a hardware token or in a KMS
  with manual approval, CI cannot sign alone, and the release job refuses to publish when the signature is missing.
  Trade-off: a human step in every release and a key ceremony for rotation, in exchange for a compromised CI
  pipeline being unable to push an update to every customer host. Decide whether key signatures go to the public
  transparency log (cosign uploads by default; `--tlog-upload=false` skips it for images, and verifiers then need
  `--insecure-ignore-tlog`). Deviate only with an ADR that names this trade-off. Source: cosign sign examples
  "sign a container image and skip uploading to the transparency log" (https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_sign.md)
  and `verify-blob --bundle ... --key cosign.pub` (https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify-blob.md),
  both verified 2026-11.
- [invariant] Whatever is signed is verified before it runs: images at admission or in the deploy step
  (`container-images` owns that), binaries by the installer or updater before exec, tools in CI before use. A
  signature that nothing verifies does not count as a control. Test: a policy or installer test with an unsigned
  artifact and one signed by another workflow or ref; both are refused. Source: keyless verification requires an
  identity and an issuer (https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify.md, verified 2026-11).

### What ships with a release

- [invariant] Every published file is in the checksum chain: `SHA256SUMS` lists every asset (binaries, packages,
  SBOMs, the verifier script), is generated last with a byte-order sort (`LC_ALL=C`), and is the signed subject.
  Every glob or loop in the release job asserts it matched the expected count. Why: a file outside the checksum file
  ships unsigned, and after a rename a glob that matches nothing lets an SBOM step pass while producing nothing.
  Test: the job compares the asset list with the `SHA256SUMS` entries and fails on any difference; renaming the
  binary on a scratch branch turns the SBOM step red. Source: reproducible with the test above.
- [default] Each artifact gets its own SBOM (syft, CycloneDX or SPDX JSON) and the release gets build provenance
  through GitHub artifact attestations (`actions/attest`, with `sbom-path` for SBOM attestations), verified with
  `gh attestation verify [file] -R [org]/[repo]`. Trade-off: attestations prove where and how an artifact was built,
  not that it is safe; alone they reach SLSA Build Level 2; private repositories use GitHub's Sigstore instance
  without a public log. Deviate only with an ADR that names this trade-off. Source: "artifact attestations are not
  a guarantee that an artifact is secure"; "by itself provides SLSA v1.0 Build Level 2"
  (https://docs.github.com/en/actions/concepts/security/artifact-attestations); `actions/attest`, permissions and
  `gh attestation verify` (https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations);
  syft multi-format output (https://github.com/anchore/syft); all verified 2026-11.
- [invariant] Release jobs install tools at an exact version from a release asset checked against a pinned checksum
  (and the vendor's signature where published): no `@latest`, no `version: latest`, no download piped into a
  shell. User-facing install instructions follow the same rule: the install script is a versioned release asset
  that verifies checksum and signature before it moves the binary into place. Why: anything that runs in a signing
  job can sign as the release. Test: `github-actions-hardening`'s checker finds no `@latest` and no pipe-to-shell;
  the install script, fed a corrupted binary, exits non-zero and installs nothing. Source: the syft README's quick
  install pipes a remote script into a shell, so the vendor default is not acceptable in a signing job
  (https://github.com/anchore/syft, verified 2026-11).
- [default] Release notes start with the verification commands for that version (signature, checksum, provenance),
  then list the changes. Trade-off: notes open with tooling instead of features. Deviate only with an ADR that names
  this trade-off. Proof: a release-job check fails when the release body does not begin with the verify block.

### Self-update and rollout

- [invariant] A self-update replaces the binary only after verification and keeps a way back: take a lock,
  download to a temp file in the install directory, verify the signature, refuse a version lower than the running
  one unless the control plane sends an explicit signed rollback, keep the previous binary, rename atomically,
  restart, health-check within a deadline, and restore the previous binary automatically when the check fails.
  Why: a bad update on hosts you cannot log into is unrecoverable without an automatic way back, and accepting
  older versions lets an attacker replay a vulnerable release. Test: three fault tests: a bad signature leaves the
  running binary untouched; a new binary that fails its health check is replaced by the previous one; an older
  version without the rollback flag is refused. Source: TUF rollback goal, "An attacker cannot trick clients into
  installing software that is older than that which the client previously knew"
  (https://theupdateframework.github.io/specification/latest/); rename(2) atomic replace
  (https://man7.org/linux/man-pages/man2/rename.2.html); both verified 2026-11.
- [invariant] Rollout records name digests: the control plane stores the exact artifact digest per platform for
  each ring, and the updater refuses an artifact whose digest differs from the record. Test: change one byte of the
  hosted artifact; every updater in the ring refuses it. Source: reproducible with the test above.
- [default] Fleets roll out in rings: an internal canary ring, then a small share of customer hosts, then the rest,
  each with a bake time and an automatic halt when health (crash loops, missed heartbeats, error rate) diverges from
  hosts still on the previous version. Rollback moves the ring back to the previous digest. Components that
  receive data from the new version deploy first. Trade-off: a full rollout takes hours or days. Deviate only with
  an ADR that names this trade-off. Test: a canary build that fails its health check halts the rollout, and the
  next ring never receives it. Source: canarying is "a partial and time-limited deployment of a change in a
  service and its evaluation" (https://sre.google/workbook/canarying-releases/, verified 2026-11).

## Procedure

1. Gate: does anything leave the build (binary, package, image, install script)? If not, this skill does not
   apply.
2. Read the release workflow, the self-updater code (if any) and the rollout configuration.
3. Version: decide the semver bump from the change; prereleases get a suffix.
4. Preflight: required gates green on the tagged commit (`github-actions-hardening`), tag signature verified,
   signing secret or identity present.
5. Build once with the reproducible settings (`go-service-baseline` for Go), then SBOM per artifact, then
   `SHA256SUMS` last, then sign and verify in the same job, then attest.
6. Images: push by digest, sign, attest, tag, re-verify (`container-images`).
7. Publish with release notes that start with the verify commands.
8. Roll out by digest through the rings; watch health against the previous version; halt or roll back on
   divergence.
9. After the last ring, verify one installed artifact end to end with the commands from the release notes.

## Traps

- A signature step with no verify step after it, or a verify regexp without anchors that accepts any workflow in
  the organisation.
- A `workflow_dispatch` rebuild that signs as `refs/heads/main` while verifiers expect `refs/tags/v`.
- `SHA256SUMS` generated before the SBOMs or the verifier script were added to `dist/`.
- A per-artifact loop whose glob still uses the old binary name after a rename and silently does nothing.
- The updater downloads the checksum from the same origin as the binary and calls that verification.
- Rolling back by re-tagging an old build instead of pointing the ring at the old digest.
- `latest` set on a prerelease because the tagging rule did not distinguish suffixes.
- The vendor's quick-install line for a signing tool copied into the release job.
- A rollout that starts with the sending side when the receiving side has not deployed the new message shape.

## Done when

- Release tags are immutable and protected; prereleases never reach the stable channel.
- Every asset is listed in a signed `SHA256SUMS`, verified in the same job; images are signed by digest.
- SBOMs and provenance exist for each artifact and `gh attestation verify` passes on a downloaded copy.
- The self-updater's three fault tests pass; its trust anchor ships inside the binary.
- Rollout records are digests, rings have bake times and halt automatically, and rollback was exercised once.
- Release notes start with commands a user can run to verify the release.

## References

- [references/release-pipeline.md](references/release-pipeline.md): load when writing or reviewing the release job:
  order of steps, checksum chain, keyless sign and verify, attestations, release notes block.
- [references/self-update-and-rings.md](references/self-update-and-rings.md): load when building or reviewing a
  self-updater, offline key handling, rollout rings, halt criteria and rollback.

## Sources

- https://semver.org/: immutability of released versions, prereleases, verified 2026-11.
- https://git-scm.com/docs/git-tag: signed tags, `gpg.format`, verification, verified 2026-11.
- https://github.com/sigstore/cosign/blob/v3.1.4/README.md: keyless signing, bundles, digest signing, verified
  2026-11.
- https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_sign.md,
  https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify.md,
  https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify-blob.md: key signing, transparency-log options,
  identity flags, verified 2026-11.
- https://docs.github.com/en/actions/concepts/security/artifact-attestations: limits of attestations, SLSA level,
  Sigstore instances, verified 2026-11.
- https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations:
  `actions/attest`, permissions, `gh attestation verify`, verified 2026-11.
- https://github.com/anchore/syft: SBOM formats, install options, verified 2026-11.
- https://theupdateframework.github.io/specification/latest/: arbitrary installation and rollback goals, verified
  2026-11.
- https://sre.google/workbook/canarying-releases/: canary definition and evaluation, verified 2026-11.
- https://man7.org/linux/man-pages/man2/rename.2.html: atomic replace, verified 2026-11.
