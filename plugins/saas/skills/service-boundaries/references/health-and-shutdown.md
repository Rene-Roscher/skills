# Health and shutdown

Source for probe semantics: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
(verified 2026-10). Quotes: "If a container fails its liveness probe more times than the configured tolerance,
the kubelet restarts that container." On readiness failure the EndpointSlice controller "removes the Pod's IP
address from the EndpointSlices of all Services that match the Pod." "Incorrect implementation of liveness probes
can lead to cascading failures."

## Endpoints

| Endpoint | Answers | Must not check |
|---|---|---|
| liveness (`/livez` or `/healthz`) | the process runs and its main loop is not stuck | databases, brokers, upstreams |
| readiness (`/readyz`) | this replica can serve now: not draining, buffers below the high mark, delivery failure rate below threshold | dependencies every replica shares |
| startup | boot finished (migrations checked, caches warm) | anything slow that should not delay restarts |

## Readiness inputs

- Process-local saturation: buffer fill by bytes and count, in-flight requests against the concurrency limit,
  recent delivery failure rate.
- Hysteresis: go unready after N consecutive bad checks, back to ready after N good ones. One slow check must
  not flap the pod.
- Draining: set on SIGTERM, before anything else.

## Shared dependencies

The Kubernetes docs describe a readiness probe that "additionally checks that each required back-end service is
available". For a dependency that every replica shares, that removes all replicas at once. Keep it out of
readiness: return 503 with `Retry-After` on the endpoints that need it, and keep the others serving. Deviating
needs an ADR.

## Shutdown order

Each step has its own timeout. The pod's `terminationGracePeriodSeconds` exceeds their sum.

1. Mark draining; readiness now fails.
2. Wait for the load balancer to stop routing (a few readiness periods).
3. Stop accepting new work; finish in-flight requests and jobs.
4. Close listeners.
5. Flush producers and buffers to the broker or the durable spool.
6. Close clients and connections.
7. Deregister from the control plane with a short timeout.

Run the binary as PID 1 in exec form so it receives SIGTERM itself; a shell wrapper as PID 1 can swallow the
signal.

## Tests

- Liveness stays OK while a downstream is stubbed down.
- Readiness flips after N bad checks and recovers after N good ones.
- SIGTERM sets draining before listeners close.
- Shutdown with in-flight work and a buffered result: the result arrives.
- Shared dependency down: readiness OK, dependent endpoint 503 with `Retry-After`, other endpoint 200.
