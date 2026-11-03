# Admission, signatures, secrets and migration order

## Signature verification at admission

Pick one admission engine and enforce it per namespace.

- Sigstore policy-controller: label the namespace `policy.sigstore.dev/include: "true"` and write a
  `ClusterImagePolicy` whose image glob covers your registry path and whose authority is the CI signing identity
  (keyless issuer and subject) or a public key. The controller also resolves tags to digests at admission.
- Kyverno `verifyImages`: a `ClusterPolicy` with the same identity; `mutateDigest` and `verifyDigest` are on by
  default, so tags are rewritten to digests and digest-less images are flagged.
- Flux `OCIRepository.spec.verify` checks signed OCI artifacts that Flux pulls (manifests, charts). It does not
  check the images pods run. Use it in addition, not instead.

Proof: deploy an unsigned image and an image signed by another identity; both are rejected. Run this after every
policy change.

## Enforcing the baseline beyond PSA

Pod Security Admission covers the Restricted controls. Rules it does not cover (read-only root filesystem, memory
limit present, image from the own registry, no `latest`) go into a `ValidatingAdmissionPolicy` or the admission
engine above, first in audit or warn mode, then enforced after the existing workloads pass.

## Secrets

- SOPS through GitOps: see `infrastructure-as-code`.
- External Secrets Operator: one `ExternalSecret` per consumer namespace, all reading the same key in the external
  store. The store is the single source; rotation happens there.
- Sealed Secrets: sealed per namespace and name; a second namespace needs its own sealed object made from the same
  source value by the seal script, never by copying a decrypted value by hand.
- Mount as files where the app supports it; environment variables end up in crash dumps and child processes.
- Grant `get` on Secrets only to the service accounts that need them; the `view` ClusterRole does not include
  Secrets.

## Migration order

| Deploy tool | Mechanism |
|---|---|
| Argo CD | Job with `argocd.argoproj.io/hook: PreSync` and a delete policy; or sync waves |
| Helm | Job with `"helm.sh/hook": pre-upgrade,pre-install` and `before-hook-creation` |
| Flux | Migration Job in its own Kustomization with `wait: true`; the app Kustomization `dependsOn` it; the Job carries `kustomize.toolkit.fluxcd.io/force: enabled` so a new image recreates it |

Migrations connect to the primary directly, not through a transaction-mode pooler, with lock and statement
timeouts set for that connection only. Every migration is expand and contract: add columns and tables first, ship
code that uses them, remove old ones in a later release.
