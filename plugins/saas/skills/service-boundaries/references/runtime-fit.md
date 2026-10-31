# Runtime fit and measurement

Numbers here are either sourced (with a date) or come from your own run. Re-check sourced limits against the
docs for the version in your lockfile.

## What to measure

| Number | Where it comes from |
|---|---|
| p50, p95, p99 latency per endpoint or job | APM traces or access logs with durations |
| Throughput (requests or jobs per second) at the plateau | the load test |
| CPU time per request, and wall time minus CPU time | profiler; a large gap means waiting, not computing |
| Memory per worker | process metrics under load |
| Queue wait time (enqueue to start) | job timestamps |
| Concurrent open connections, fan-out rate | connection server metrics |
| Database time per request | query log or APM spans |

Commit the load script under `bench/` with a README that says how to reproduce the run (data volume, target,
concurrency, duration). Quote only numbers produced by that script or by CI.

## Little's law worked through

Concurrency L = throughput λ × time in system W.

An invoicing app's PDF endpoint calls a rendering API that takes 2 s. The FPM pool has `pm.max_children = 50`.

- Maximum throughput λ = L / W = 50 / 2 s = 25 requests per second.
- At 40 requests per second, requests queue in front of FPM until they time out, while CPU stays low.
- A Go rewrite that calls the same API synchronously from a pool of 50 has the same limit. A rewrite with 2,000
  goroutines raises it, but so does moving the call to a queue job and returning 202.

Use the deployment's real worker counts: `pm.max_children` per pool and pod count for FPM, the worker count for
Octane, queue worker processes per queue. `pm.max_children` "sets the limit on the number of simultaneous
requests that will be served" (https://www.php.net/manual/en/install.fpm.configuration.php, verified 2026-10).

## Fixes to try inside the runtime first

- Query and index fixes; caching validated values.
- Move slow or external work to a queue; separate queues by urgency so bulk work does not delay urgent jobs.
- Octane after a state audit (`laravel-production-runtime`). Octane "boots your application once, keeps it in
  memory, and then feeds it requests" (https://laravel.com/docs/12.x/octane, verified 2026-10).
- Reverb for WebSockets, with `ext-uv` and horizontal scaling (below).
- More workers or pods, once the calculation shows slots are the limit.

## Sourced limits

| Component | Limit and lever | Source |
|---|---|---|
| Reverb event loop | default `stream_select` loop "is typically limited to 1,024 open files"; for more than about 1,000 concurrent connections install `ext-uv`, which Reverb uses automatically when available | https://laravel.com/docs/12.x/reverb (verified 2026-10) |
| Reverb scaling | `REVERB_SCALING_ENABLED=true` with a dedicated central Redis; Reverb servers behind a load balancer | same page |
| Open files and ports | `ulimit -n`, the web server's connection limits and the local port range also cap connections | same page |
| PHP-FPM | `pm.max_children` caps simultaneous requests | https://www.php.net/manual/en/install.fpm.configuration.php (verified 2026-10) |

## When another runtime fits

- Many long-lived connections with per-connection backpressure or edge auth: Go or Node.
- Thousands of concurrent outbound calls, or a static binary for hosts you do not control: Go.
- Raw sockets or custom wire protocols as a product feature: Go or Rust.
- CPU-bound transforms where per-item latency or memory per worker is the measured limit: Rust or Go, or a
  native tool called per job.
