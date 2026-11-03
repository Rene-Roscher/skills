# SOPS with age, and GitOps sources

## .sops.yaml

```yaml
creation_rules:
  - path_regex: clusters/prod/.*\.sops\.yaml$
    encrypted_regex: ^(data|stringData)$
    age: >-
      age1prodcontroller...,
      age1offlinebackup...
  - path_regex: clusters/staging/.*\.sops\.yaml$
    encrypted_regex: ^(data|stringData)$
    age: >-
      age1stagingcontroller...,
      age1offlinebackup...
```

The backup recipient's private key is kept offline, apart from the operator keys, and tested twice a year:
`SOPS_AGE_KEY_FILE=[backup key file] sops -d [file]` in a clean shell.

## Rotation

- Add a recipient: edit `.sops.yaml`, run `sops updatekeys -y [file]` per file.
- Remove a recipient: edit `.sops.yaml`, `sops updatekeys -y [file]`, then `sops rotate -i [file]`. If the key may
  be compromised, also rotate the secret values at their source.
- Record each rotation with date and reason.

## Sealing without plaintext on disk

A seal script reads values from the environment or a hidden prompt, writes the plaintext into a `mktemp -d`
directory removed by `trap ... EXIT`, encrypts into the repo path and never writes plaintext there. `.gitignore`
ignores everything secret-like and re-admits only `*.sops.yaml` and `*.example`. A secret scanner (for example
gitleaks) runs in pre-commit and CI.

## GitOps sources and promotion

- One repo path per environment. Image automation may write only to non-production paths, with a deploy key
  limited to that repo.
- Production moves by a pull request that bumps a pinned version or digest after staging is healthy.
- Pin images by digest in production overlays; see `kubernetes-workloads` for signature checks at admission.
- Flux: `prune: true`, `dependsOn` for real ordering, `wait: false` only with a comment. Argo CD: automated sync
  with `prune` and `selfHeal` on, so live drift is reverted and visible.
- After an emergency `kubectl` change, commit the same change before the next reconcile reverts it.
