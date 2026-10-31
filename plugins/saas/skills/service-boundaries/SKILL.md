---
name: service-boundaries
description: "Decides whether to move work from a PHP/Laravel monolith into Go, Rust or Node on measured numbers, and designs the boundary: dumb workers, smart control plane, pull-only links, versioned contracts, per-service keys. Use when someone proposes a microservice, worker or rewrite, PHP seems too slow, APP_KEY is shared between services, or writing CONTRACT.md. Not for splitting code in one app."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
  verified: "2026-10"
---

# Service boundaries

This skill decides whether a piece of work leaves the PHP monolith, and if it does, how the boundary is built so
that it stays safe and changeable: who decides, who connects to whom, what the wire contract is, how payloads are
encrypted and how health is reported. Framework syntax for Octane, Reverb and queues stays with the Laravel docs
and `laravel-production-runtime`. The failure it prevents: a rewrite that moves the same bottleneck into a second
runtime and adds a failure domain, a contract nobody owns, and a shared application key.

## Applies when / does not apply

- Applies: someone proposes a microservice, worker, sidecar, probe or agent, or a rewrite in Go, Rust or Node;
  PHP seems too slow for WebSockets, long-lived connections, many concurrent outbound calls, CPU-heavy work or raw
  networking; encrypted payloads or `APP_KEY` are shared between services; worker registration, heartbeats or
  config sync are being designed; a `CONTRACT.md`, protobuf or JSON schema between repos is being written.
- Does not apply: splitting code inside one Laravel app (`laravel-architecture`), Kubernetes manifests, language
  syntax questions. Public marketing pages are always a separate deployment (`web-architecture`). Vendor or
  build decisions belong to `build-vs-buy`.

## Rules

### Decide with numbers

- [default] Measure before you extract. Bring a profile or trace and a load test that show the bottleneck in
  numbers, try the in-runtime fixes first, and write an ADR with the baseline, the target and the condition under
  which you would revert.
  Trade-off: a measurement round delays the decision by days. Deviate only with an ADR that names this trade-off.
  Source: https://laravel.com/docs/12.x/octane ("Octane boots your application once, keeps it in memory, and then
  feeds it requests") (verified 2026-10).

- [invariant] Compute the capacity limit before blaming the language. Concurrency = throughput × latency (Little's
  law). PHP-FPM's `pm.max_children` caps simultaneous requests, so an endpoint that waits 2 s on an upstream with
  50 children tops out at 25 requests per second, whatever the CPU does.
  Why: long waits exhaust process slots, not CPU; a faster language with the same blocking design hits the same
  wall.
  Test: the ADR shows the calculation with the deployment's real `pm.max_children` (or Octane worker count) and
  the measured latency, and the load test reproduces the plateau.
  Source: https://www.php.net/manual/en/install.fpm.configuration.php ("sets the limit on the number of
  simultaneous requests that will be served") (verified 2026-10).

- [default] Use the runtime-fit table below and quote only numbers you have a source or a measurement for.
  Trade-off: no quick answer from folklore; each row needs a source or a run. Deviate only with an ADR that names
  this trade-off. Source: https://laravel.com/docs/12.x/reverb (verified 2026-10).

| Workload | Try in PHP first (known limit) | Extract when | Typical target |
|---|---|---|---|
| CRUD, dashboards, admin, business rules | FPM or Octane; database and cache fixes | practically never | stays |
| WebSockets, live streams | Reverb on a ReactPHP loop. The default `stream_select` loop is "typically limited to 1,024 open files"; above about 1,000 connections install `ext-uv`; scale out with `REVERB_SCALING_ENABLED` and a central Redis | measured Reverb limits are not enough, or you need edge auth without an app round trip and per-connection backpressure | Go or Node relay |
| Many concurrent outbound calls, connectors on customer hosts | queue workers, one job per process slot | thousands of concurrent calls, sub-second timing, a static binary for hosts you do not control | Go |
| Raw sockets and custom wire protocols (packet-level tools, protocol parsers) | possible with privileges, poor timing control | as soon as it is a product feature | Go or Rust |
| CPU-heavy transforms (images, compression, large file parsing) | queue plus more workers, or a native tool per job | per-item latency or memory per worker is the measured limit | Rust or Go |
| Public marketing and product pages | not in the app | always a separate deployment | Nuxt or Next |
| Headless browser automation | none | when needed | Node (Playwright) |

- [default] Do not extract when the code is a business decision (billing, permissions, tenancy, rules,
  notifications), the bottleneck is the database, the boundary would need a distributed transaction, nobody owns
  the second runtime's on-call, patching and release signing, measured traffic is below a tuned monolith's
  capacity, or the only argument is language speed.
  Trade-off: the monolith keeps work that a specialist runtime might do faster. Deviate only with an ADR that
  names this trade-off and answers each point. Test: the ADR has a "why not keep it in the monolith" section.

### Shape of the boundary

- [default] Dumb worker, smart brain. Extracted workers execute and report raw signals. Every business decision
  (thresholds, state machines, notifications, sharding, compiling product features into primitive jobs) lives in
  the control plane. Workers have no database access, and states only the control plane computes never appear on
  the wire.
  Trade-off: more data on the wire and the control plane on the hot path. Deviate only with an ADR that names
  this trade-off. Test: in the worker repo, `go list -deps ./... | grep -E 'database/sql|pgx|lib/pq|go-sql-driver'`
  prints nothing; a contract test shows the wire enum excludes control-plane-only states.

- [default] Pull-only connectivity. Workers dial the control plane: register, pull config by content hash,
  heartbeat. Commands (sync now, drain) ride back on the heartbeat response. The control plane never connects
  into workers. A duplicate worker ID evicts the older connection. Planned shutdown sends a bounded deregister.
  Trade-off: commands wait for the next heartbeat. Deviate only with an ADR that names this trade-off.
  Test: a worker registers, receives config, gets "not modified" on an equal hash, picks up a change on the next
  pull and deregisters on SIGTERM.

- [invariant] The wire format is a contract artifact. Each side keeps a `CONTRACT.md` with fields, types, units,
  nullability, endpoints, auth and status semantics. Evolution is additive only: never rename or retype. Consumers
  ignore unknown fields and accept both shapes during a rollout. A schema version has an accept band (N and N-1).
  The deploy order is written down: consumer first, control plane before data plane.
  Why: there is no shared build between repos, so a one-sided change silently stops ingestion or registration.
  Test: consumer contract tests run against golden fixtures produced by the producer's real encoder; generated
  schemas are checked for drift in CI; for protobuf, `buf breaking` against the main branch blocks the merge.
  Source: https://buf.build/docs/breaking/usage/ (verified 2026-10).

- [invariant] Numbers both sides must agree on (maximum message size, batch size, interacting timeouts) live once
  in the shared contract and are enforced on both sides: the sender drops an oversized item, the receiver closes.
  Why: a sender cap larger than the receiver's limit makes every oversized batch fail on arrival.
  Test: both sides import the constant; a test fails when a literal duplicate of it appears in either repo.

### Encryption between services

- [invariant] Each service relationship gets its own encryption key. The application's own `APP_KEY` never leaves
  the application. On the Laravel side construct `new Illuminate\Encryption\Encrypter($key, 'aes-256-cbc')` (or
  `aes-256-gcm`) with the cipher passed explicitly: the constructor defaults to `aes-128-cbc`. The interop
  packages' examples read `APP_KEY`, and the Node package falls back to `process.env.APP_KEY` when no key is
  given, so always pass the dedicated key. A service that must read Laravel's own cookies or sessions is the one
  exception, recorded in an ADR with the risk.
  Why: whoever holds `APP_KEY` can forge signed URLs and read every `encrypted` cast, so a compromised service
  would be a compromised application.
  Test: a grep guard finds no `APP_KEY` in service config, env templates or worker source outside the app's own
  config; the app fails at boot when the dedicated key is missing.
  Source: https://github.com/laravel/framework/blob/12.x/src/Illuminate/Encryption/Encrypter.php,
  https://github.com/Rene-Roscher/laravel-node-encryption (verified 2026-10).

- [invariant] Across services use only `encryptString` and `decryptString` with your own JSON. Never call
  `decrypt()` or `Crypt::decrypt()` on data from another service.
  Why: `decrypt($payload, $unserialize = true)` runs `unserialize()` without a class allowlist, so a compromised
  service holding the key can plant a serialized PHP object.
  Test: an architecture test allows the cross-service encrypter only through `encryptString` and
  `decryptString`; a grep guard in the other repos rejects the serialize path (Go `.Encrypt(` and `.Decrypt(`,
  Rust and Node `encrypt(` and `decrypt(`) unless an allowlist entry gives a reason.
  Source: https://github.com/laravel/framework/blob/12.x/src/Illuminate/Encryption/Encrypter.php (verified 2026-10).

- [invariant] Encryption does not stop replay. Payloads to and from critical services carry an `exp` that the
  producer sets and the receiver enforces. The contract defines which services are critical: anything that grants
  access, moves money, changes configuration or carries credentials. Where a replay inside the validity window
  still matters, add a purpose or audience and a single-use `jti` that the receiver consumes atomically.
  Why: a captured ciphertext decrypts just as well a week later.
  Test: an expired payload is rejected, a payload for another purpose is rejected, and a second use of the same
  `jti` is rejected (atomic consume, for example `SET NX` with a TTL).

- [default] Other cross-service payloads carry `exp` as well.
  Trade-off: clock skew handling for payloads where replay is harmless. Deviate only with an ADR that names this
  trade-off, or a one-line reason in the contract. Test: a payload type without `exp` fails the contract test
  unless the contract gives the reason.

- [invariant] Transport stays TLS; payload encryption is an extra layer for places where TLS ends (message logs,
  caches, queues). Rotate with a list of previous keys, keep decrypt errors opaque to callers, and fail closed: a
  secret that is present but cannot be decrypted fails the operation instead of silently degrading.
  Why: a job that skips an undecryptable credential and runs anyway reports a wrong result as a real one.
  Test: an old-key payload decrypts after rotation and new payloads use the new key; the caller sees one generic
  error; an undecryptable credential fails the job.
  Source: `Encrypter::previousKeys()` in the framework source above; previous keys in all three interop packages,
  https://github.com/Rene-Roscher/laravel-go-encryption (verified 2026-10).

- [default] Use one maintained interop library per language and prove compatibility in CI with vectors produced
  by the real counterpart, in both directions, over the Laravel majors you run.
  Trade-off: a dependency per language instead of a small hand-written port. Deviate only with an ADR that names
  this trade-off. Source: the three packages test both directions against the real Laravel encrypter for Laravel
  10 to 13, https://github.com/Rene-Roscher/laravel-rust-encryption (verified 2026-10).

### Health, bounds and shutdown

- [invariant] Liveness reflects only the process. Readiness reflects whether this replica can serve now:
  process-local saturation (buffer fill, delivery-failure rate) with hysteresis, plus draining on SIGTERM.
  Why: Kubernetes restarts a container that fails liveness and removes a failing-readiness pod from Service
  endpoints; its docs warn that incorrect liveness probes can cause cascading failures.
  Test: liveness stays OK while a downstream is down; readiness flips only after N consecutive bad checks and
  back after N good ones; SIGTERM sets draining before listeners close.
  Source: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ (verified 2026-10).

- [default] Keep dependencies that every replica shares out of readiness. When one is down, fail the affected
  requests with 503 and `Retry-After` instead of marking all replicas unready.
  Trade-off: the Kubernetes docs suggest readiness may check required back-ends; for a shared dependency that
  drains the whole fleet at once, including endpoints that do not need it. Deviate only with an ADR that names
  this trade-off. Test: with the shared dependency stubbed down, readiness stays OK, the affected endpoint returns
  503 with `Retry-After`, an unaffected endpoint returns 200.

- [invariant] Bound everything that crosses the boundary: concurrency (a semaphore with non-blocking dispatch and
  a shed counter), buffers (by bytes and count, drop oldest, count drops), a timeout on every network call, request
  body caps. Delivery is at-least-once with a durable spool; consumers are idempotent by key.
  Why: an unbounded buffer turns a downstream outage into an out-of-memory crash, and a blocking dispatch lets
  one slow batch stall every other schedule.
  Test: fill each buffer past its cap and assert the drop counter; deliver the same message twice and assert one
  effect.

- [default] Shut down in order, each step with its own timeout: mark draining, wait for the load balancer to stop
  routing, finish in-flight work, close listeners, flush producers and buffers, close clients. The orchestrator's
  grace period exceeds the sum, and the binary runs as PID 1 so it receives the signal.
  Trade-off: slower rollouts. Deviate only with an ADR that names this trade-off. Test: a shutdown with in-flight
  work and a buffered result delivers that result.

- [default] A new runtime ships with an owner and the monolith's operational floor: CI with tests and a race or
  sanitizer run, a pinned toolchain, signed release artifacts and an SBOM (`container-images`), dependency
  vulnerability scanning, structured logs without personal data, errors-only tracking with PII off, metrics with
  bounded labels, and a correlation ID propagated across the boundary.
  Trade-off: weeks of setup before the first production deploy. Deviate only with an ADR that names this
  trade-off. Test: the ADR checklist links each CI job, and each job exists before the first deploy.

## Procedure

1. Gate: is there a measured bottleneck? No profile, trace or load test means no extraction decision yet. Plan
   the measurement (references/runtime-fit.md) and stop.
2. Read the installed framework versions from the lockfile (Laravel, Octane, Reverb) and check the docs for those
   versions before quoting any limit. If no docs tool is available, mark the limit Unverified.
3. Do the Little's-law calculation with the deployment's real worker counts.
4. Try the in-runtime fixes and measure again.
5. Still a gap: fill the runtime-fit row and the "do not extract" checks in the ADR (references/adr-template.md).
6. Design the boundary: control plane and worker split, pull-only protocol, `CONTRACT.md` on both sides, shared
   limits, a dedicated key and the string path, `exp` and `jti` where critical, health semantics, bounds,
   shutdown.
7. Wire the guards (references/guard-artifacts.md) before the first deploy.

## Traps

- "PHP is slow" for an endpoint that waits on the database or an upstream. A rewrite keeps the wait.
- An invented connection limit ("Reverb can only do 100 connections"). The documented limit is the
  `stream_select` file limit, and `ext-uv` plus horizontal scaling move it. Check the docs for your version.
- Copying the quickstart: the interop examples read `APP_KEY`, and `Crypt::encrypt($array)` takes the serialize
  path. Both look like the documented way.
- `new Encrypter($key)` without a cipher uses `aes-128-cbc` and rejects a 32-byte key.
- A second, hand-written decryption next to the library in another service: duplicated security code that
  drifts.
- Readiness that pings the shared database: one database blip takes every replica out of rotation at once.
- A guard test filter that matches nothing passes. Run guard suites whole and assert a minimum count.
- A contract change merged on one side only. Without a consumer test against the producer's real encoder, CI on
  both sides stays green.

## Done when

- The ADR holds the measured baseline, the calculation, the fixes tried, the target, the revert criterion and the
  owner, or the decision to stay in the monolith.
- `CONTRACT.md` exists on both sides, and the contract, interop and golden tests run in CI.
- The key, string-path, replay, health and shutdown tests pass.
- The new runtime's CI jobs exist before its first production deploy.

## References

- [references/runtime-fit.md](references/runtime-fit.md): load when assessing a workload, measuring it or working
  through Little's law.
- [references/when-not-to-extract.md](references/when-not-to-extract.md): load when someone proposes a rewrite or a
  new service.
- [references/worked-example-control-plane.md](references/worked-example-control-plane.md): load when designing
  workers, agents or any fleet that reports to the app.
- [references/contracts.md](references/contracts.md): load when writing `CONTRACT.md`, versioning, golden and
  interop tests, or protobuf checks.
- [references/cross-service-encryption.md](references/cross-service-encryption.md): load when sharing encrypted
  data between Laravel and Go, Node or Rust.
- [references/health-and-shutdown.md](references/health-and-shutdown.md): load when adding health endpoints, probes
  or graceful shutdown.
- [references/adr-template.md](references/adr-template.md): load when writing the extraction ADR.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when wiring the CI guards or a path-scoped
  rule that points here.

## Sources

- https://laravel.com/docs/12.x/reverb: event loop, `stream_select` limit, `ext-uv`, `REVERB_SCALING_ENABLED`,
  verified 2026-10.
- https://laravel.com/docs/12.x/octane: worker model, verified 2026-10.
- https://www.php.net/manual/en/install.fpm.configuration.php: `pm.max_children`, verified 2026-10.
- https://github.com/laravel/framework/blob/12.x/src/Illuminate/Encryption/Encrypter.php: default cipher,
  `decrypt()` unserialize path, `encryptString`, `previousKeys`, verified 2026-10.
- https://github.com/Rene-Roscher/laravel-go-encryption, https://github.com/Rene-Roscher/laravel-node-encryption,
  https://github.com/Rene-Roscher/laravel-rust-encryption: string and serialize APIs, previous keys, `APP_KEY`
  defaults, CI interop over Laravel 10 to 13, verified 2026-10.
- https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/: probe semantics,
  verified 2026-10.
- https://buf.build/docs/breaking/usage/: breaking-change detection, verified 2026-10.
