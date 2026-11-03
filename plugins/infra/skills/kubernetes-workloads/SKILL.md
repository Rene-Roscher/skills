---
name: kubernetes-workloads
description: "Sets the baseline for Kubernetes workloads: restricted securityContext, PSA labels, measured requests and limits, separate liveness, readiness and startup probes, default-deny NetworkPolicies, quotas, images by digest with signature checks at admission, migrations before rollout, one secret source. Use when writing or reviewing Deployments, Jobs, Helm or Kustomize. Not for cluster provisioning."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
paths:
  - "**/kustomization.yaml"
  - "**/Chart.yaml"
  - "**/values*.yaml"
  - "**/*deployment*.yaml"
---

# Kubernetes workloads

This skill decides what every workload manifest must contain before it ships: least privilege, honest probes,
resources from measurement, network isolation, a verified image, ordered migrations and one place for each secret.
Replica counts, disruption budgets, spread rules and failover belong to `high-availability`; read its Kubernetes
section and do not repeat it. How the manifests reach the cluster belongs to `infrastructure-as-code`. The failure
this prevents: a workload that runs as root with a writable filesystem, restarts in a storm when a database blips,
talks to everything in the cluster and runs whatever image a tag points to today.

## Applies when / does not apply

- Applies: a new or changed Deployment, StatefulSet, Job, CronJob, Helm chart or Kustomize overlay; a namespace
  definition; a NetworkPolicy; a migration Job; how a workload gets its secrets; a review of an existing cluster's
  workloads.
- Does not apply: node and cluster provisioning, CNI or control plane choice, failover and backup design
  (`high-availability`), GitOps repo layout (`infrastructure-as-code`), application code.

## Rules

### Pod security

- [invariant] Every container runs with `runAsNonRoot: true` and a fixed numeric UID, `allowPrivilegeEscalation:
  false`, `capabilities.drop: [ALL]`, `seccompProfile.type: RuntimeDefault`, and `readOnlyRootFilesystem: true`
  with `emptyDir` mounts for the paths it writes. Why: these are the Restricted Pod Security Standard controls,
  and a read-only root filesystem stops a compromised process from changing the image it runs. Test: the
  namespace enforces `restricted` and the pod is admitted; `kubectl exec ... touch /x` fails. Source:
  https://kubernetes.io/docs/concepts/security/pod-security-standards/ (Restricted: `allowPrivilegeEscalation`
  false, `runAsNonRoot` true, seccomp `RuntimeDefault` or `Localhost`, drop `ALL`); the standard does not require
  a read-only root filesystem, that part is design judgment. Verified 2026-11-03.
- [invariant] Every application namespace carries Pod Security Admission labels:
  `pod-security.kubernetes.io/enforce: restricted` with a pinned `enforce-version`, plus `warn` and `audit`. A
  namespace that needs less is labelled `baseline` with an ADR. Why: without labels nothing stops the next
  workload from dropping the baseline, and the same rule then holds for old and new manifests. Test: apply a pod
  without `seccompProfile` to the namespace; it is rejected. Source:
  https://kubernetes.io/docs/concepts/security/pod-security-admission/, verified 2026-11-03.
- [invariant] Images in production are referenced by digest, and the admission layer verifies their signature
  for the namespaces that run them (Sigstore policy-controller or Kyverno `verifyImages`). Signing in CI without
  verifying at admission proves nothing. Why: a tag can be moved to other content; a digest cannot. Test: deploy
  an unsigned image by digest into the namespace; admission rejects it. Source:
  https://kubernetes.io/docs/concepts/containers/images/ ("Tags can be moved to point to different images, but
  digests are fixed"), https://docs.sigstore.dev/policy-controller/overview/,
  https://kyverno.io/docs/policy-types/cluster-policy/verify-images/, verified 2026-11-03.
- [default] No `hostNetwork`, `hostPath`, `privileged` or shared host namespaces in application namespaces;
  node-level helpers live in a separate namespace with their own ADR. Trade-off: some agents need host access and
  get their own exception. Deviate only with an ADR that names this trade-off. Test: the `restricted` label
  rejects them. Source: https://kubernetes.io/docs/concepts/security/pod-security-standards/, verified 2026-11-03.

### Probes

- [invariant] Liveness checks only that the process can make progress, never a database, cache, queue or other
  service. Readiness may check what the pod needs to serve. Use separate endpoints. Why: a liveness probe that
  depends on a shared service restarts every replica at once when that service blips. Test: block the database
  from one pod; it turns unready and is not restarted. Source: Kubernetes docs, "The readiness and liveness probes
  do not depend on each other to succeed" and "Readiness probes run on the container during its whole lifecycle"
  (https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/,
  verified 2026-11-03); the restart-storm effect is reproducible with the test above.
- [invariant] A liveness probe must be able to fail: for a worker without HTTP, check a heartbeat the work loop
  updates, not that the process name exists. Why: a check that only finds the process never detects a hung
  worker. Test: pause the work loop in a test build; the pod restarts within `failureThreshold × periodSeconds`.
  Source: reproducible with the test above.
- [invariant] Slow starters get a `startupProbe` instead of a long `initialDelaySeconds` on liveness. Why: the
  docs say that once the startup probe succeeds "the liveness probe takes over to provide a fast response to
  container deadlocks". Test: a cold start that takes 60 seconds is not killed, and a deadlock after start is
  detected at the liveness period. Source: same Kubernetes probes page, verified 2026-11-03.

### Resources and scaling

- [invariant] Requests come from measured usage (for example the p95 of a week of real traffic), memory has a
  limit, and runtimes with their own heap limit set it below the container limit (`GOMEMLIMIT`, JVM max heap).
  Why: requests below real use overcommit nodes and invite evictions; memory beyond the limit "may get killed".
  Test: the request is within a stated margin of the measured value, with the query that measured it in a comment.
  Source: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/, verified 2026-11-03.
- [invariant] An HPA needs requests on the metric it scales on, and the manifest under GitOps does not set
  `spec.replicas` once the HPA owns it. Why: without a request "the autoscaler will not take any action for that
  metric", and an applied `replicas` value fights the HPA. Test: `kubectl describe hpa` shows current utilization,
  not `unknown`. Source: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/, verified
  2026-11-03.
- [invariant] Each namespace has a `ResourceQuota` and a `LimitRange` with default requests. Why: one runaway
  workload otherwise takes a node's memory, and with a quota "the control plane may reject admission" for pods
  without requests. Test: a pod without requests receives the defaults. Source:
  https://kubernetes.io/docs/concepts/policy/resource-quotas/, verified 2026-11-03.
- [invariant] Availability settings (at least two replicas, a PodDisruptionBudget that allows one eviction,
  `topologySpreadConstraints` across nodes and zones, graceful shutdown) follow the Kubernetes rules in
  `high-availability`. Singletons such as a scheduler run one replica with `strategy: Recreate`. Why: two
  scheduler pods during a rolling update run every job twice. Test: drain a node; the PDB lets pods move one at a
  time and the service keeps answering; during a scheduler rollout only one pod exists at any moment. Source:
  https://kubernetes.io/docs/tasks/run-application/configure-pdb/ and
  https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ (verified 2026-11-01 in
  `high-availability`).

### Network

- [invariant] Each namespace starts from a default-deny NetworkPolicy for ingress and egress, then allows DNS,
  metrics scraping and each dependency port by name. Check every selector against the live labels before
  applying. Why: a pod that no policy selects accepts and sends everything, and a wrong selector cuts traffic
  silently. Test: from a debug pod in another namespace, the service port is unreachable; the application's own
  calls still work. Source: https://kubernetes.io/docs/concepts/services-networking/network-policies/ (the
  `default-deny-all` example; policies need a network plugin that implements them), verified 2026-11-03.
- [default] Roll out policies per workload (`podSelector` on that workload) before the namespace-wide deny.
  Trade-off: a window in which other pods stay open. Deviate only with an ADR that names this trade-off. Source:
  reproducible with the test above.

### Rollout order and secrets

- [invariant] Schema migrations run to completion before the new application version receives traffic, and are
  expand and contract so the old version keeps working on the new schema. Use the deploy tool's ordering: an Argo
  CD `PreSync` hook, a Helm `pre-upgrade` hook, or a Flux Kustomization for the migration Job that the app
  Kustomization `dependsOn`, with `kustomize.toolkit.fluxcd.io/force: enabled` so the Job is recreated per
  release. Why: a Job applied next to the Deployment is not ordered against it. Test: a release whose migration
  fails leaves the old pods serving and the new ReplicaSet absent. Source:
  https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/, https://helm.sh/docs/topics/charts_hooks/,
  https://fluxcd.io/flux/components/kustomize/kustomizations/, verified 2026-11-03.
- [invariant] Secrets reach the cluster through an encrypted or external mechanism (SOPS through GitOps, Sealed
  Secrets, External Secrets Operator), never as plaintext in git. Why: by default Secrets are "stored
  unencrypted" in etcd and anyone who can create a pod in the namespace can read them, so access to the namespace
  is access to the secret. Test: `git grep` over the repo finds no `kind: Secret` with plain `data`. Source:
  https://kubernetes.io/docs/concepts/configuration/secret/, verified 2026-11-03.
- [invariant] Each credential has one source object. Workloads reference it with `secretKeyRef` or `envFrom`;
  another namespace gets it by a sync from that source, never by a second copy of the value. Why: copies drift at
  the first rotation. Test: grep the decrypted secrets for duplicate values across objects; none. Source:
  reproducible with the test above.
- [default] Workloads that read config or secrets from environment variables roll on change (a checksum
  annotation or a reloader controller). Trade-off: a config change restarts pods. Deviate only with an ADR that
  names this trade-off. Test: change a ConfigMap value; the pods restart with the new value. Source: reproducible.

## Procedure

1. Gate: is this a workload manifest or namespace? If it is provisioning or failover, use the other skill.
2. Render the manifests (`helm template`, `kustomize build`) and review the rendered output, not the templates.
3. Walk the rules in order: security, probes, resources, network, rollout, secrets. Use
   [references/workload-template.md](references/workload-template.md) as the target shape.
4. Validate offline: `kubeconform -strict` against the cluster version, a policy linter (kube-linter, Polaris or
   the admission policies themselves in audit mode), then `kubectl apply --dry-run=server` where the reviewer's
   credentials allow it (it persists nothing, but needs write permission).
5. Report findings by severity with the manifest diff. Do not apply.

## Traps

- Signing images in CI and never checking signatures at admission.
- The same `/up` endpoint for liveness and readiness, with a database call behind it.
- A queue worker's liveness probe that greps the process list.
- Memory requests set below measured use "because the nodes are full".
- Namespaces without PSA labels "for now", which lets later workloads skip the baseline.
- A NetworkPolicy whose label selector matches nothing in the live cluster.
- A migration Job with an immutable spec that blocks every later sync until it is deleted.
- One password copied into Secrets in two namespaces.
- `spec.replicas` left in a manifest after adding an HPA.

## Done when

- The namespace enforces `restricted` and every pod is admitted under it.
- Liveness, readiness and startup probes check different things, and liveness depends on nothing shared.
- Requests cite their measurement; the namespace has a quota and defaults.
- Default-deny is in place and the allowed paths were tested.
- Images are pinned by digest and admission rejects an unsigned image.
- Migrations complete before rollout; each secret has one source.

## References

- [references/workload-template.md](references/workload-template.md): load when writing a new workload or
  namespace, or when comparing a manifest against the target shape.
- [references/admission-and-secrets.md](references/admission-and-secrets.md): load when setting up signature
  verification, admission policies, External Secrets or migration ordering.

## Sources

- https://kubernetes.io/docs/concepts/security/pod-security-standards/ and
  https://kubernetes.io/docs/concepts/security/pod-security-admission/: Restricted controls, namespace labels,
  verified 2026-11-03.
- https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/: probe
  independence, startup probes, verified 2026-11-03.
- https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/,
  https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/,
  https://kubernetes.io/docs/concepts/policy/resource-quotas/: limits, HPA, quotas, verified 2026-11-03.
- https://kubernetes.io/docs/concepts/services-networking/network-policies/: default deny, plugin support,
  verified 2026-11-03.
- https://kubernetes.io/docs/concepts/containers/images/: digests, verified 2026-11-03.
- https://docs.sigstore.dev/policy-controller/overview/ and
  https://kyverno.io/docs/policy-types/cluster-policy/verify-images/: signature checks at admission, verified
  2026-11-03.
- https://kubernetes.io/docs/concepts/configuration/secret/: Secret storage and access, verified 2026-11-03.
- https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/, https://helm.sh/docs/topics/charts_hooks/ and
  https://fluxcd.io/flux/components/kustomize/kustomizations/: `PreSync`, `pre-upgrade`, `dependsOn`, force
  recreate, verified 2026-11-03.
