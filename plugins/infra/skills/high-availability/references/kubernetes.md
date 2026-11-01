# Hosting on Kubernetes

## Contents

- Failure domains in a cluster
- Replicas, spread and budgets
- Probes and graceful shutdown
- Stateful workloads
- Control plane, ingress and add-ons
- Review checklist

## Failure domains in a cluster

Name them before you add replicas: pod, node, zone, cluster, provider account. A cluster with all nodes in one zone
survives a node loss but not a zone loss. The cluster as a whole (control plane, operators, ingress controller,
DNS inside the cluster) is a failure domain too; if the requirement is to survive its loss, the answer is a second
cluster or a standby path, not more replicas inside it.

## Replicas, spread and budgets

- A Deployment's `replicas` defaults to one. Source:
  https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ (verified 2026-11-01).
- Spread rules: `topologySpreadConstraints` take `maxSkew`, `topologyKey`, `whenUnsatisfiable` (`DoNotSchedule` is
  the default, `ScheduleAnyway` prefers but allows skew) and an optional `minDomains`. Only one constraint may exist
  per `topologyKey` and `whenUnsatisfiable` pair. Typical keys: `topology.kubernetes.io/zone` and
  `kubernetes.io/hostname`. Source:
  https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ (verified 2026-11-01).
- The constraint's `labelSelector` must match the workload's own pods, or it spreads nothing.
- PodDisruptionBudget: set `minAvailable` or `maxUnavailable` (one of them), as a number or a percentage. It limits
  voluntary evictions through the Eviction API. It does not prevent involuntary disruptions, though those count
  against the budget, and deleting a Deployment or Pod bypasses it. Rolling updates of a Deployment are governed by
  its own `maxUnavailable` and `maxSurge`, not by the budget. Zero allowed evictions blocks node drains. Source:
  https://kubernetes.io/docs/tasks/run-application/configure-pdb/,
  https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ (verified 2026-11-01).
- The disruptions page recommends the `AlwaysAllow` unhealthy pod eviction policy so that misbehaving pods can still
  be evicted during a drain. Source: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ (verified
  2026-11-01).
- Stateless frontends: a budget such as `minAvailable: 90%` or `maxUnavailable: 1` keeps capacity during drains.
  Single-instance stateful workloads: the docs offer no budget (accept downtime) or `maxUnavailable: 0` plus a
  human agreement; neither is high availability.
- Capacity: enough free resources must exist on the surviving nodes or zones to run all replicas after a loss. State
  the headroom (for example, N+1 nodes) in the inventory.

Starting point for a three-replica web workload (adapt names; this is a pattern, not a full manifest):

```yaml
spec:
  replicas: 3
  template:
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels: { app: web }
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels: { app: web }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  maxUnavailable: 1
  unhealthyPodEvictionPolicy: AlwaysAllow
  selector:
    matchLabels: { app: web }
```

## Probes and graceful shutdown

- Readiness decides whether a pod receives Service traffic. Liveness decides whether the kubelet restarts the
  container. Startup probes protect slow starts so liveness does not kill them. Source:
  https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ (verified
  2026-11-01).
- Liveness checks the process only. A liveness check that fails when the database is down restarts the whole fleet
  during a database incident (design judgment).
- On termination the kubelet runs a `preStop` hook if one exists, then sends SIGTERM, then SIGKILL after
  `terminationGracePeriodSeconds` (default 30 seconds). Endpoint removal runs in parallel with shutdown, so a short
  `preStop` sleep or drain delay avoids sending traffic to a pod that is already stopping. Source:
  https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ (verified 2026-11-01).
- The application must stop accepting new work on SIGTERM, finish in-flight requests, and exit before the grace
  period. Queue workers finish or release the current job. Test with a request loop during a rolling update.

## Stateful workloads

- Databases use an operator that handles failover (see database-storage.md); do not hand-roll a StatefulSet with a
  single replica and call it highly available.
- Persistent volumes: know whether the storage class is zonal. A pod can be rescheduled to another zone only if its
  volume can follow, or if the data is replicated at the application level.
- Redis or queue brokers used for state: decide whether loss is acceptable (cache) or not (queue, sessions) and size
  persistence and replication to match.

## Control plane, ingress and add-ons

- Managed control planes usually span zones; self-managed ones need three members across zones.
- Run at least two ingress controller replicas, spread, with a budget.
- Cluster DNS, the CNI, the certificate manager and the secrets operator are single points of failure for
  everything. Give them replicas and budgets too.
- Keep the manifests in Git and the cluster rebuildable. Back up what cannot be rebuilt: secrets not in a secret
  manager, custom resources with live state, and persistent volumes.
- Auto-update paths must point at what actually serves traffic. A pipeline that bumps image tags for a deployment that
  is disabled leaves the live one stale (design judgment, from a real audit pattern).

## Review checklist

- Every critical workload: replicas of at least two, zone and node spread, a budget that allows one eviction.
- Readiness probe on every serving container; liveness without external dependencies; startup probe where start is slow.
- SIGTERM handled, grace period longer than the slowest request.
- Headroom after losing a node or a zone is stated.
- Cluster add-ons have replicas and budgets.
- `scripts/ha_check.py` run over rendered manifests, findings triaged.
