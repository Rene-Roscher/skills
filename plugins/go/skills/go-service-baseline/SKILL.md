---
name: go-service-baseline
description: "Production baseline for Go services and workers: cmd/internal layout, fail-fast config, context and graceful shutdown, errgroup with bounded concurrency, jittered retries, slog, private metrics registry, race and fuzz gates that can fail, pinned linters, reproducible static builds. Use when starting, reviewing or hardening a Go service or daemon. Not for wire formats (cross-service-contracts)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
paths:
  - "**/go.mod"
  - "**/*.go"
---

# Go service baseline

This skill sets the floor for a long-running Go process: how it is laid out, how it starts, how it stops, how it
bounds its own work, how it reports, and which CI gates prove all of that. Go syntax and library APIs stay in the
Go docs. Wire formats shared with other repos belong to `cross-service-contracts`, the decision to extract a service
at all to `service-boundaries`, image builds to `container-images`, and workflow permissions to
`github-actions-hardening`. The failure it prevents: a service that runs on a typo'd default, loses in-flight work
on every deploy, grows without bound when a downstream is slow, and ships through CI gates that cannot fail.

## Applies when / does not apply

- Applies: a new Go service, worker, agent or daemon; reviewing `main.go`, config loading, shutdown, goroutine
  lifecycles, retries, logging, metrics, HTTP server setup; Go CI (tests, race, fuzz, lint, vulnerability scan);
  making Go builds reproducible; persisting credentials or state to disk.
- Does not apply: the field layout, versioning and tests of a format another repo reads (`cross-service-contracts`);
  whether to write the service in Go at all (`service-boundaries`); Dockerfile and base image (`container-images`);
  release signing and fleet rollout (`release-supply-chain`); one-off scripts and CLIs that exit in seconds.

## Rules

Ordered by blast radius. Examples use a worker that pulls jobs, runs checks and publishes results.

### Startup and lifecycle

- [invariant] Config is parsed and validated once at startup, and every invalid value stops the process: a value
  that does not parse, a missing required key, an out-of-range number, a non-positive duration and an unknown key
  (YAML `KnownFields(true)`, JSON `DisallowUnknownFields`) are startup errors that name the key. Never fall back to
  a default on a parse error. The loader takes its inputs (`args`, a `getenv` function) as parameters.
  Why: a helper that returns the default when parsing fails turns a typo into a silent misconfiguration, and a
  negative interval panics later inside `time.NewTicker`. Test: a table test feeds `-5s`, `abc`, an empty required
  value and a misspelled key; each returns an error naming the key, and `main` exits non-zero.
  Source: `time.NewTicker`: "The duration d must be greater than zero; if not, NewTicker will panic."
  (https://pkg.go.dev/time#NewTicker, verified 2026-11).
- [invariant] Every function that blocks takes `ctx context.Context` as its first parameter and honours it, and every
  network call gets its own deadline derived from that context. Work that must outlive the caller (a result that
  must still be published after the request ends) uses `context.WithoutCancel` plus its own timeout, with a comment
  saying why. Why: an unbounded call turns a slow dependency into a stuck goroutine and a shutdown that never ends.
  Test: a fake dependency that never answers; the call returns `context.DeadlineExceeded` within its budget.
  Source: package `context`: "The Context should be the first parameter, typically named ctx"; `WithoutCancel` "is
  not canceled when parent is canceled" (https://pkg.go.dev/context, verified 2026-11).
- [invariant] Shutdown starts from `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)` in `main` and runs in
  order, each step with its own timeout: readiness reports draining, wait for the load balancer to notice, stop
  accepting (`http.Server.Shutdown`), wait for in-flight work, flush producers and buffers, close clients. The sum
  stays below the orchestrator's grace period. Hijacked connections (WebSockets) are closed through
  `RegisterOnShutdown`. Why: closing the publisher before the pool drains drops the results the deploy was supposed
  to keep. Test: send SIGTERM while a job is in flight; readiness fails first, the job's result is published, the
  process exits 0 inside the budget. Source: `Shutdown` "does not attempt to close nor wait for hijacked connections
  such as WebSockets" (https://pkg.go.dev/net/http#Server.Shutdown); `NotifyContext`
  (https://pkg.go.dev/os/signal#NotifyContext), both verified 2026-11.
- [invariant] Every goroutine has an owner that waits for it. Long-running loops (scheduler, config sync,
  heartbeat, HTTP server) run under one `errgroup.WithContext`; each returns `ctx.Err()` on cancellation; the first
  error cancels the rest and `Wait` hands over to the ordered shutdown. No bare `go func()` without a join.
  Why: orphan goroutines leak, keep writing after their sink is closed, and hide errors in a log line.
  Test: `goleak.VerifyTestMain(m)` in every package that starts goroutines. Source: errgroup "The derived Context is
  canceled the first time a function passed to Go returns a non-nil error or the first time Wait returns"
  (https://pkg.go.dev/golang.org/x/sync/errgroup); https://github.com/uber-go/goleak; both verified 2026-11.
- [invariant] No global mutable state: package-level variables hold constants or values that never change after
  init. Clock, filesystem, RNG, HTTP client, metrics registry and policies (for example an egress allow-list) are
  passed through constructors. Tests switch behaviour by injecting a different policy, never through an exported
  `SetXForTest` toggle. Why: a global switch leaks between parallel tests and can stay on in a production build.
  Test: two instances with different policies run in parallel tests under `-race` and each sees only its own
  policy; a CI grep rejects `func Set\w*ForTest` and `promauto.New` in non-test code.
  Source: reproducible with the test above.

### Bounds and failure

- [invariant] Concurrency and buffers are bounded. Fan-out uses `errgroup.SetLimit` or a semaphore; a scheduling
  loop that must not stall dispatches with `TryGo` (or a non-blocking send) and counts what it sheds. Every queue
  and buffer has a cap by count and bytes, a stated overflow policy (drop oldest, drop newest or reject) and a
  counter. Why: an unbounded buffer turns a downstream outage into an out-of-memory crash, and a blocking dispatch
  lets one slow batch delay every other job. Test: fill each buffer past its cap; the drop counter rises and heap
  stays flat. Source: `TryGo` "calls the given function in a new goroutine only if the number of active goroutines
  in the group is currently below the configured limit" (https://pkg.go.dev/golang.org/x/sync/errgroup, verified
  2026-11).
- [invariant] HTTP servers set `ReadHeaderTimeout`, `IdleTimeout` and `MaxHeaderBytes`, and wrap request bodies in
  `http.MaxBytesReader`. A server that streams long responses documents why `WriteTimeout` is unset. Why: with both
  header and read timeouts at zero there is no timeout, and slow clients hold goroutines open. Test: a client that
  sends headers one byte per second is disconnected after `ReadHeaderTimeout`; an oversized body gets 413.
  Source: `ReadHeaderTimeout`: "If negative, or if zero and ReadTimeout is zero or negative, there is no timeout."
  (https://pkg.go.dev/net/http#Server, verified 2026-11).
- [default] Retries use capped exponential backoff with full jitter (sleep a random duration between zero and
  `min(cap, base × 2^attempt)`), honour `Retry-After`, and retry only idempotent operations or requests that carry
  an idempotency key. RNG and clock are injected. Trade-off: slower recovery for a single client, in exchange for a
  fleet that does not reconnect in the same second after a control-plane restart. Deviate only with an ADR that
  names this trade-off. Test: with a seeded RNG every delay is inside its window; a create request without an
  idempotency key is not retried after a 5xx. Source: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
  (jittered backoff versus plain exponential, verified 2026-11).
- [default] Workers that process untrusted input recover panics per task, turn them into an error with context,
  count them and report them. Trade-off: a recovered panic can hide a bug if nobody reads the counter. Deviate only
  with an ADR that names this trade-off. Test: inject a task implementation that panics; the worker survives, the
  next task runs, the panic counter is 1. Source: reproducible with the test above.
- [invariant] Credentials and state files are written atomically: create a temp file in the same directory, write,
  `fsync`, set mode `0600` (directory `0700`), `rename` over the target, `fsync` the directory. Why: a crash during
  `os.WriteFile` leaves a truncated credential, and rename is atomic only within one filesystem. Test: a fake
  filesystem fails between write and rename; the old file is intact and readable. Source: rename(2): "If newpath
  already exists, it will be atomically replaced"; `EXDEV` across mounts
  (https://man7.org/linux/man-pages/man2/rename.2.html, verified 2026-11).

### Observability

- [default] Logs go through `log/slog` as JSON to stdout, the level is adjustable at runtime with `slog.LevelVar`,
  and the logger is injected. Tokens, keys and personal data never appear; log a short hash prefix instead of a
  token and mask client addresses. Library and per-job code logs at debug only. Trade-off: less detail in incident
  logs. Deviate only with an ADR that names this trade-off. Test: a capturing `slog.Handler` in tests; a test that
  runs a job with a known token asserts the token string is absent from every record.
  Source: https://pkg.go.dev/log/slog (verified 2026-11).
- [invariant] Metrics live in a private registry: `prometheus.NewRegistry()`, collectors built with
  `promauto.With(reg)` or registered on `reg`, served by `promhttp.HandlerFor(reg, ...)` on an internal listener.
  Labels take values from a fixed set (map errors to slugs); per-entity series are deleted when the entity leaves.
  Why: top-level `promauto` constructors register globally and panic on conflict, so importing a package can crash
  a binary or a test run. Test: construct two service instances in one test process without a panic; a cardinality
  test asserts the label values come from the declared set. Source: promauto: "simply importing another package
  can trigger a panic" (https://pkg.go.dev/github.com/prometheus/client_golang/prometheus/promauto, verified
  2026-11).
- [invariant] Liveness reports only that the process is alive; readiness reports whether this replica can take
  work now (local saturation with hysteresis, draining after SIGTERM). Neither depends on a dependency shared by
  every replica. Health and metrics run on a listener separate from public traffic. Why: a liveness check on a
  shared database restarts the whole fleet during one database blip. Test: stub the shared dependency down;
  liveness and readiness stay OK, affected requests return 503 with `Retry-After`. Source: the semantics are owned
  by `service-boundaries`; https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
  (verified 2026-11).

### Tests and CI gates

- [default] Decision logic lives in pure functions (no IO, injected clock) with table-driven tests; IO stays at the
  edges. Trade-off: more small types and constructor parameters. Deviate only with an ADR that names this
  trade-off. Source: https://go.dev/wiki/TableDrivenTests (verified 2026-11).
- [invariant] Every CI test run uses `go test -race -count=1 ./...` with cgo enabled for that step. Why: the race
  detector only sees code paths that run, and it needs cgo, so a job-wide `CGO_ENABLED=0` meant for static builds
  breaks it. Test: a seeded racy test in a scratch branch turns the job red. Source: "The race detector requires
  cgo to be enabled" and "only finds races that happen at runtime" (https://go.dev/doc/articles/race_detector,
  verified 2026-11).
- [invariant] Every parser of untrusted bytes has a fuzz target with seeds and a property (no panic, typed error,
  policy never weakened). CI runs each target in its own `go test -run='^$' -fuzz='^FuzzX$' -fuzztime=[budget]`
  invocation, asserts it found at least one target, and fails on a crash: no `|| true`, no `continue-on-error`.
  Crashers land in `testdata/fuzz/` and are committed. Why: `-fuzz` must match exactly one target in one package,
  and an error-masked fuzz step can never fail. Test: a fuzz target that panics on one seed turns the job red.
  Source: `-fuzz` "must match exactly one package within the main module, and regexp must match exactly one fuzz
  test within that package" (https://pkg.go.dev/cmd/go); failing input "will now be run by default with go test"
  (https://go.dev/doc/security/fuzz/), both verified 2026-11.
- [invariant] Linters and scanners run at pinned versions: golangci-lint with a `version: "2"` config and an exact
  version in CI, `govulncheck` installed as `golang.org/x/vuln/cmd/govulncheck@vX.Y.Z` and run in text mode in each
  module directory. Why: a floating linter breaks unrelated builds on its release day, and govulncheck exits 0 in
  `-json`, SARIF and OpenVEX modes regardless of findings. Test: `grep -rn '@latest\|version: latest' .github/`
  prints nothing; a module with a known-vulnerable call makes the job red. Source: golangci-lint: "install a
  specific version" so builds don't "fail all at the same time" (https://golangci-lint.run/docs/welcome/install/ci/);
  govulncheck exit codes (https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck), both verified 2026-11.
- [invariant] Release builds are static and reproducible: the toolchain is pinned to a patch version (a `toolchain`
  line plus `GOTOOLCHAIN=local` against a pinned installer or builder image), `CGO_ENABLED=0`, `-trimpath`,
  `GOWORK=off`, `GOFLAGS=-mod=readonly`, and `make build`, the image build and the release all use the same
  environment. A CI job builds twice in clean directories and compares SHA-256. `-ldflags -X` targets the full
  import path of an uninitialized string variable. Why: with `GOTOOLCHAIN=auto` the go command may download a
  different toolchain, a leaked `go.work` makes the shipped binary differ from the tested one, and `-X` on a
  variable with a computed initializer does nothing. Test: the double-build job; `[binary] version` prints the
  injected version. Source: Go 1.21 and later "the Go toolchain is perfectly reproducible", cgo and the current
  directory are the inputs to remove (https://go.dev/blog/rebuild); toolchain switching
  (https://go.dev/doc/toolchain); `-X` "will not work if the initializer makes a function call"
  (https://pkg.go.dev/cmd/link); all verified 2026-11.
- [default] Layout: `cmd/[binary]/main.go` only wires dependencies; one `internal/[concern]` package per
  responsibility; `pkg/` only for a separately versioned module that other repos import, such as a wire contract.
  The runtime image is distroless static, non-root, binary as PID 1 (`container-images`). Trade-off: more packages
  and no shell in the image for debugging. Deviate only with an ADR that names this trade-off. Source: "Since other
  projects cannot import code from our internal directory, we're free to refactor its API"
  (https://go.dev/doc/modules/layout, verified 2026-11).

## Procedure

1. Gate: is this a long-running process (service, worker, agent)? If it is a short CLI, apply only the build and
   CI rules.
2. Read `go.mod` for the Go version and the `toolchain` line; read the CI workflow for the Go setup and gates.
3. Config: one loader, injected `getenv`, every key validated, unknown keys rejected. Table test.
4. `main`: `NotifyContext`, construct dependencies, one `errgroup`, ordered shutdown with budgets.
5. Bounds: limits on fan-out, caps and counters on every buffer, deadlines on every network call, server timeouts.
6. Observability: injected `slog` logger, private registry, liveness and readiness on an internal listener.
7. CI: `-race`, `goleak`, fuzz per target, pinned golangci-lint and govulncheck, double-build reproducibility.
   Each gate gets a seeded failure once to prove it can go red.
8. Hand the image to `container-images` and the release to `release-supply-chain`.

## Traps

- A `getEnvInt` helper that returns the default when `strconv.Atoi` fails. Every typo becomes the default.
- `CGO_ENABLED=0` set at job level for the static build also disables `-race` in the test step of the same job.
- `go test -run 'TestA|TestB'` exits 0 when a rename means nothing matches. Assert a minimum test count or run the
  package whole.
- A fuzz step ending in `|| true`, or a loop over fuzz targets that finds none and still passes.
- Passing the request context into an async producer: the request ends, the context is cancelled, and healthy
  records in the same batch fail with it.
- `http.Server.Shutdown` returns while WebSocket handlers are still running; they need `RegisterOnShutdown`.
- Not calling `stop()` from `signal.NotifyContext` once shutdown begins: until then a second interrupt does not
  trigger the default exit, so an operator cannot kill a hung shutdown with a second Ctrl-C.
- `govulncheck -json` in CI looks like a gate and always exits 0.
- `GOFLAGS=-mod=readonly` only reports an error "if go.mod needs to be updated"; modules missing from the cache
  still download. When the build must be offline, run `go mod download` first and build with `GOPROXY=off`
  ("no communication should be attempted"), or vendor (https://go.dev/ref/mod, verified 2026-11).
- `golangci-lint` with a v1 config under a v2 binary, or `version: latest` in the action.

## Done when

- Invalid config fails at startup with the key named, proven by a table test.
- A SIGTERM test with in-flight work shows readiness off first, work completed, exit 0 inside the budget.
- `goleak` runs in every package that starts goroutines; no global mutable state or test toggles remain.
- Every buffer has a cap and a drop counter; every network call has a deadline; servers set header timeouts.
- CI runs race, fuzz per target, pinned golangci-lint and govulncheck, and a reproducibility check, and each gate
  was seen red once.

## References

- [references/lifecycle-skeleton.md](references/lifecycle-skeleton.md): load when writing or reviewing `main.go`,
  the config loader, shutdown order, bounded worker pools, retries or the atomic file writer.
- [references/ci-gates.md](references/ci-gates.md): load when writing the Go CI workflow, the fuzz loop, lint and
  vulnerability gates, the reproducibility job or the guard greps.

## Sources

- https://pkg.go.dev/os/signal#NotifyContext: signal-driven cancellation, verified 2026-11.
- https://pkg.go.dev/context: ctx first, `WithoutCancel`, verified 2026-11.
- https://pkg.go.dev/golang.org/x/sync/errgroup: `WithContext`, `SetLimit`, `TryGo`, verified 2026-11.
- https://pkg.go.dev/net/http#Server: timeouts, `Shutdown`, `RegisterOnShutdown`, verified 2026-11.
- https://pkg.go.dev/time#NewTicker: panic on non-positive duration, verified 2026-11.
- https://pkg.go.dev/github.com/prometheus/client_golang/prometheus/promauto: global registration and panics,
  verified 2026-11.
- https://github.com/uber-go/goleak: `VerifyTestMain`, verified 2026-11.
- https://go.dev/doc/articles/race_detector: runtime-only detection, cgo requirement, overhead, verified 2026-11.
- https://pkg.go.dev/cmd/go and https://go.dev/doc/security/fuzz/: `-fuzz`, `-fuzztime`, corpus behaviour,
  `-trimpath`, verified 2026-11.
- https://golangci-lint.run/docs/welcome/install/ci/ and https://golangci-lint.run/docs/configuration/file/:
  pinned versions, `version: "2"`, verified 2026-11.
- https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck: exit codes, verified 2026-11.
- https://go.dev/blog/rebuild, https://go.dev/doc/toolchain, https://pkg.go.dev/cmd/link: reproducibility,
  toolchain selection, `-X`, verified 2026-11.
- https://man7.org/linux/man-pages/man2/rename.2.html: atomic replace, `EXDEV`, verified 2026-11.
- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/: jittered backoff, verified 2026-11.
- https://go.dev/doc/modules/layout: `cmd/` and `internal/`, verified 2026-11.
