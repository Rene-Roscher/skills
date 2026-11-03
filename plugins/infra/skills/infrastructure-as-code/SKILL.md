---
name: infrastructure-as-code
description: "Sets change rules for infrastructure code: OpenTofu with encrypted, locked remote state, bounded provider pins and deletion protection; idempotent Ansible with host key checking and per-admin logins; SOPS with several age recipients; GitOps with promotion between environments. Use when writing or reviewing .tf, playbooks, .sops.yaml or Flux/Argo config. Not for pod specs (kubernetes-workloads)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
paths:
  - "**/*.tf"
  - "**/*.tofu"
  - "**/.terraform.lock.hcl"
  - "**/ansible.cfg"
  - "**/.sops.yaml"
---

# Infrastructure as code

This skill decides how infrastructure changes are written, reviewed and applied: one owning tool per layer,
OpenTofu for provisioning, Ansible for hosts outside the cluster, SOPS with age for secrets in git, and a GitOps
controller for everything inside the cluster. Tool syntax stays with the vendor docs linked under Sources.
Failover design belongs to `high-availability`, pod specs to `kubernetes-workloads`. The failure this prevents: a
change applied from a laptop with a stale local state, a plaintext secret or an unreviewed plan, which destroys
something that cannot be rebuilt.

## Applies when / does not apply

- Applies: writing or reviewing `.tf` files, backends, provider pins or lifecycle blocks; Ansible roles,
  inventories and `ansible.cfg`; `.sops.yaml` and encrypted files; Flux or Argo CD sources, Kustomizations and
  image automation; CI for any of these; an agent asked to change infrastructure.
- Does not apply: Deployment and pod settings (`kubernetes-workloads`), failover and backup design
  (`high-availability`), edge proxy config (`edge-proxy-tls`), plain HCL or YAML syntax questions, cost estimates.

## Rules

### Change safety

- [invariant] Agents treat infrastructure as read-only. Reading files and running `tofu plan`, `--check --diff`,
  `kubectl get/describe` and `flux diff` is fine; every apply, playbook run, reconcile, push, secret seal, import,
  state edit or delete needs a person's approval for that one change. Enforce it with credentials, not prose: a
  kubeconfig bound to the `view` ClusterRole, a plan-only cloud token, a hook that blocks apply commands. Why:
  infrastructure mistakes are often irreversible and a GitOps controller acts on every push. Test: ask the agent to
  "fix the firewall rule"; it returns a diff and a plan and stops before `tofu apply`. Source: Kubernetes RBAC,
  `view` "does not allow viewing Secrets" (https://kubernetes.io/docs/reference/access-authn-authz/rbac/, verified
  2026-11-03); the stop-before-apply part is reproducible with the test above.
- [invariant] Check the live system before stating a fact about it, and find the deployed copy before editing:
  trace the pipeline that renders and ships the file. Delete dead copies instead of keeping them as reference.
  Why: a stale directory once led to the conclusion "no backups", and an edit to a dead config copy changed
  nothing in production. Test: in a repo with two copies of one config, the agent names the copy the deploy job
  renders, with the path of that job, before proposing an edit. Source: reproducible with the test above.
- [invariant] One owning tool per layer (image build, provisioning, host config, cluster reconcile), and one owner
  per attribute. When a second controller manages an attribute (a failover daemon moving an IP, an autoscaler
  setting replicas), the IaC side leaves it out or lists it in `ignore_changes`. Why: two owners revert each
  other and the plan never comes clean. Test: right after an apply, `tofu plan -detailed-exitcode` exits 0.
  Source: https://opentofu.org/docs/cli/commands/plan/ (exit code 2 means changes present), verified 2026-11-03.

### OpenTofu

- [invariant] State lives in a remote backend with locking and object versioning, never in git or only on one
  disk. Why: state holds every secret OpenTofu touched in plaintext, local state cannot be locked and dies with the
  disk. Test: `git ls-files '*.tfstate*'` is empty; while one `tofu apply` waits at its prompt, a second run fails
  to acquire the lock. Source: https://opentofu.org/docs/language/settings/backends/s3/ (`use_lockfile`, "highly
  recommended that you enable Bucket Versioning"), verified 2026-11-03.
- [invariant] State and plan files are encrypted with OpenTofu's `encryption` block, `enforced = true` on `state`
  and `plan`, the key from a KMS or a long passphrase kept outside the repo, and the key backed up before the
  first encrypted write. Why: the docs say OpenTofu "does not and cannot protect the sensitive values in the state
  file" from whoever runs it, so encryption guards the stored copy, and a lost key means a lost state. Test: the
  stored state object has no readable `resources` list; with the key variable unset, `tofu plan` fails instead of
  writing plaintext. Source: https://opentofu.org/docs/language/state/encryption/ (`enforced`, `fallback`, key
  loss), verified 2026-11-03.
- [invariant] Root modules bound every provider above and below (`~>`) and commit `.terraform.lock.hcl`;
  reusable modules state minimums only. Why: an open `>=` pulls the next major release at the next `init`.
  Test: no `required_providers` entry lacks `~>` or `<`, and the lock file is tracked. Source:
  https://opentofu.org/docs/language/expressions/version-constraints/ and
  https://opentofu.org/docs/language/files/dependency-lock/, verified 2026-11-03.
- [invariant] Anything that must never be rebuilt (servers with local data, volumes, addresses customers point
  at, DNS zones, resources on terms that cannot be bought again) carries `prevent_destroy = true` and the
  provider's own delete and rebuild protection, and CI fails any plan that deletes or replaces it. Why:
  `prevent_destroy` "cannot prevent the remote object from being destroyed" once the block is removed. Test: delete
  the resource block; the CI check over `tofu show -json` reports the `delete` action and fails. Source:
  https://opentofu.org/docs/language/resources/behavior/, verified 2026-11-03.
- [invariant] Inputs of long-lived servers do not float: no `most_recent = true` image lookup or templated
  `user_data` that changes on a refresh, or the attribute is in `ignore_changes`. Why: a new upstream image plans
  a replacement of a server that holds data. Test: after a new image is published, `plan` shows no replace.
  Source: reproducible with the test above.
- [invariant] Changes reach infrastructure only through a plan reviewed in CI on the pull request and an apply of
  that saved plan. A scheduled job runs `tofu plan -detailed-exitcode` and alerts on exit code 2. No console
  clicks. Why: manual drift is invisible until the next apply undoes it. Test: change a tag in the provider
  console; the drift job alerts. Source: https://opentofu.org/docs/cli/commands/plan/, verified 2026-11-03.
- [default] Tokens are `sensitive = true` variables fed from the secret store; every resource carries labels for
  owner and environment. Trade-off: more variables to wire. Deviate only with an ADR that names this trade-off.
  Source: reproducible: `tofu plan` output shows `(sensitive value)` for the token.

### Ansible

- [invariant] Host key checking stays on. Known host keys come from provisioning output or an SSH certificate
  authority. Why: the docs say checking "guards against server spoofing and man-in-the-middle attacks". Test:
  `ansible-config dump --only-changed` shows no `HOST_KEY_CHECKING=False`; a host with a changed key fails.
  Source: https://docs.ansible.com/ansible/latest/inventory_guide/connection_details.html, verified 2026-11-03.
- [invariant] Each admin connects with an own key or SSH certificate as a named user with sudo; no fleet-wide
  shared root key and no `remote_user = root`. Why: one shared key cannot be revoked for one person and the logs
  name nobody. Test: removing one admin's key leaves the others working; `auth.log` names the person. Source:
  reproducible with the test above.
- [invariant] Roles are idempotent and a production run is previewed. A second run reports `changed=0`;
  `--check --diff --limit [one host]` runs first, then `serial: 1` as a canary; config files use `validate:`
  (for example `sshd -t -f %s`). Why: check mode is only as good as module support ("Modules that do not support
  check mode report nothing and do nothing"), so the canary carries the rest. Test: two runs against a throwaway
  host; the second has `changed=0`. Source: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html
  and https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html, verified 2026-11-03.

### Secrets with SOPS and age

- [invariant] Every encrypted file has at least two age recipients: the key that the controller or operator uses
  and an offline backup recipient stored apart from it. Recipients are set in `.sops.yaml` `creation_rules`, not
  on the command line. Why: with one recipient, one lost key file loses every secret. Test: in a clean shell with
  only the backup key in `SOPS_AGE_KEY_FILE`, `sops -d` succeeds on every file. Source:
  https://getsops.io/docs/usage/identities/age/ (comma-separated recipients), verified 2026-11-03.
- [invariant] Removing a recipient is `sops updatekeys` followed by `sops rotate -i`, and the secret values
  themselves are rotated when the removed key may be compromised. Why: SOPS warns that without rotation "owners of
  the removed key may have add access to the data key in the past". Test: after removal, the old key cannot
  decrypt a freshly rotated file. Source: https://getsops.io/docs/usage/key-management/, verified 2026-11-03.
- [invariant] Plaintext secrets never sit in the repo working tree: values come from a prompt or environment into
  a temp directory removed by a trap, `.gitignore` admits only encrypted and example files, and a secret scanner
  runs in pre-commit and CI. Why: ignored plaintext files still get copied, synced and read by tools. Test:
  `git status --ignored` lists no plaintext secret; the scanner over full history is clean. Source: reproducible
  with the test above.
- [default] One recipient set per environment, so a staging key cannot decrypt production. Trade-off: more keys
  to back up. Deviate only with an ADR that names this trade-off. Test: the staging key fails on a production file.
  Source: reproducible with the test above.

### GitOps

- [invariant] Git is the only write path: the controller reconciles from git with pruning, and an emergency
  `kubectl` change is committed at once. Push an encrypted secret before relying on reconcile. Why: the
  controller reverts live patches and reads the remote, not the working tree. Test: `flux diff kustomization` or
  `argocd app diff` reports no drift after the incident. Source: reproducible with the test above.
- [invariant] Builds land in a non-production environment first; production changes by a reviewed promotion that
  bumps a pinned version or digest. Image automation writes only to non-production paths and uses a key that
  cannot change cluster definitions. Why: automation that ships every main build to production makes CI the
  release gate. Test: a new image tag changes only staging files. Source:
  https://fluxcd.io/flux/use-cases/gh-actions-helm-promotion/ ("When the Pull Request is merged, Flux upgrades the
  Helm release on the production cluster"), verified 2026-11-03.
- [default] Order with `dependsOn` (CRDs and operators before their resources) and set `wait: false` only where
  waiting deadlocks, with a comment saying why. Trade-off: slower first sync. Deviate only with an ADR that names
  this trade-off. Source: reproducible: a fresh cluster syncs from empty without manual steps.

## Procedure

1. Gate: name the layer and its owning tool, find the deployed copy, and confirm the live state matches the repo.
2. Classify the resources the change touches; mark the ones that must never be rebuilt.
3. Write the change as a diff. Load the matching reference below for the tool.
4. Run the read-only preview: `tofu plan -out`, `ansible-playbook --check --diff --limit`, `flux diff`.
5. Read the preview for delete, replace, recipient or secret changes. Any of these needs a named approval.
6. Hand the diff, the preview and the rollback step to the owner. Do not apply.

## Traps

- A `.gitignore` entry for `*.tfstate` reads as safe while the state, with provider tokens, sits unencrypted and
  unlocked on one laptop.
- `prevent_destroy` is removed together with the block it protects.
- An S3-compatible store that ignores conditional writes accepts `use_lockfile` without locking anything. Prove
  the lock with two concurrent runs.
- `host_key_checking = False` added "for new hosts" stays forever.
- Check mode shows green for tasks whose modules skip it.
- A single age key used for the fleet and the cluster, with no backup recipient and no rotation note.
- Image automation with write access to the repo that defines the clusters.
- Docs that contradict the live config. Trust the live system, then fix or delete the doc.

## Done when

- State is remote, locked, versioned and encrypted with `enforced = true`; the key has a backup.
- Providers are bounded, the lock file is committed, irreplaceable resources have both protections.
- CI plans every PR and a drift job runs on a schedule.
- Ansible keeps host key checking, logs in per admin, and passes the second-run `changed=0` test.
- Every SOPS file decrypts with the backup key alone.
- Production changes only through a reviewed promotion, and nothing was applied by the agent.

## References

- [references/opentofu.md](references/opentofu.md): load when writing backends, encryption, lifecycle blocks or
  the CI plan and drift jobs.
- [references/ansible.md](references/ansible.md): load when writing roles, `ansible.cfg` or a production rollout.
- [references/secrets-gitops.md](references/secrets-gitops.md): load when setting up SOPS recipients, rotation,
  Flux or Argo CD sources and promotion.

## Sources

- https://opentofu.org/docs/language/state/encryption/: encryption block, `enforced`, `fallback`, key loss,
  verified 2026-11-03.
- https://opentofu.org/docs/language/settings/backends/s3/: `use_lockfile`, bucket versioning, verified 2026-11-03.
- https://opentofu.org/docs/language/resources/behavior/: `prevent_destroy` and its limit, verified 2026-11-03.
- https://opentofu.org/docs/language/expressions/version-constraints/ and
  https://opentofu.org/docs/language/files/dependency-lock/: `~>` in root modules, lock file in git, verified
  2026-11-03.
- https://opentofu.org/docs/cli/commands/plan/: `-detailed-exitcode`, `-out`, `-lock-timeout`, verified 2026-11-03.
- https://docs.ansible.com/ansible/latest/inventory_guide/connection_details.html,
  https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html,
  https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html: host keys, check and
  diff mode, `validate`, verified 2026-11-03.
- https://getsops.io/docs/usage/identities/age/ and https://getsops.io/docs/usage/key-management/: recipients,
  `updatekeys`, `rotate`, verified 2026-11-03.
- https://fluxcd.io/flux/use-cases/gh-actions-helm-promotion/: staged promotion by pull request, verified
  2026-11-03.
- https://kubernetes.io/docs/reference/access-authn-authz/rbac/: `view` ClusterRole, verified 2026-11-03.
