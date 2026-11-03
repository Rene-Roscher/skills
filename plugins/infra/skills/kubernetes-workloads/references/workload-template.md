# Workload target shape

## Contents

- Deployment and namespace
- Namespace defaults
- Workload kinds

## Deployment and namespace

A rendered Deployment and namespace that meet the rules. Values marked "measured" come from real usage; the
numbers below are placeholders, not recommendations.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: shop
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.33   # the cluster's minor version
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: shop
spec:
  # no replicas field when an HPA owns the count
  selector:
    matchLabels: {app: api}
  strategy:
    rollingUpdate: {maxUnavailable: 0, maxSurge: 1}
  template:
    metadata:
      labels: {app: api}
    spec:
      automountServiceAccountToken: false   # unless the app calls the API server
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
        seccompProfile: {type: RuntimeDefault}
      terminationGracePeriodSeconds: 30     # longer than the slowest request or job
      containers:
        - name: api
          image: registry.example.com/shop/api@sha256:[digest]
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: {drop: [ALL]}
          env:
            - name: GOMEMLIMIT          # runtime heap cap below the container limit
              value: "400MiB"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef: {name: api-db, key: password}   # the one source object
          resources:
            requests: {cpu: 200m, memory: 384Mi}   # measured, query in a comment
            limits: {memory: 512Mi}
          startupProbe:
            httpGet: {path: /livez, port: 8080}
            failureThreshold: 30
            periodSeconds: 2
          livenessProbe:
            httpGet: {path: /livez, port: 8080}     # process only, no dependencies
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet: {path: /readyz, port: 8080}    # may check what serving needs
            periodSeconds: 5
          volumeMounts:
            - {name: tmp, mountPath: /tmp}
      volumes:
        - name: tmp
          emptyDir: {sizeLimit: 64Mi}
```

Add the PodDisruptionBudget and `topologySpreadConstraints` from `high-availability`.

## Namespace defaults

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: default-deny-all, namespace: shop}
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: api-allow, namespace: shop}
spec:
  podSelector: {matchLabels: {app: api}}
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: ingress}}
      ports: [{port: 8080}]
  egress:
    - to:
        - namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: kube-system}}
          podSelector: {matchLabels: {k8s-app: kube-dns}}   # check the live labels
      ports: [{port: 53, protocol: UDP}, {port: 53, protocol: TCP}]
    - to:
        - podSelector: {matchLabels: {app: postgres}}
      ports: [{port: 5432}]
---
apiVersion: v1
kind: LimitRange
metadata: {name: defaults, namespace: shop}
spec:
  limits:
    - type: Container
      defaultRequest: {cpu: 100m, memory: 128Mi}
      default: {memory: 256Mi}
---
apiVersion: v1
kind: ResourceQuota
metadata: {name: quota, namespace: shop}
spec:
  hard: {requests.cpu: "8", requests.memory: 16Gi, limits.memory: 24Gi, pods: "60"}
```

Before applying a policy, list the live labels of every selector target
(`kubectl get pods -A --show-labels`, `kubectl get ns --show-labels`) and compare. Reference manifests copied from
elsewhere often name labels the cluster does not use.

## Workload kinds

- Web: as above, HPA on CPU or requests per second.
- Queue worker: liveness on a heartbeat file or counter that the loop updates; grace period longer than the
  longest job; idempotent jobs so a killed job can retry.
- Scheduler or other singleton: `replicas: 1`, `strategy: Recreate`, so two never run at once.
- Database on local storage: requests equal limits (Guaranteed QoS), required anti-affinity; see
  `high-availability`.
