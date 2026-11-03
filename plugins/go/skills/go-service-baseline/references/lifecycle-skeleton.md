# Lifecycle skeleton

## Contents
- `main.go` wiring
- Config loader
- Ordered shutdown
- Bounded pool with shedding
- Retry with full jitter
- Atomic credential write

Sketches, not a framework. Names are examples; error handling is shortened where it adds nothing.

## `main.go` wiring

```go
func main() {
	if err := run(context.Background(), os.Args[1:], os.Getenv, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1) // defers do not run after os.Exit; flush error reporting before this line
	}
}

func run(parent context.Context, args []string, getenv func(string) string, out io.Writer) error {
	cfg, err := config.Load(args, getenv)
	if err != nil {
		return fmt.Errorf("config: %w", err)
	}
	ctx, stop := signal.NotifyContext(parent, os.Interrupt, syscall.SIGTERM)
	defer stop()

	log := slog.New(slog.NewJSONHandler(out, &slog.HandlerOptions{Level: cfg.LogLevel}))
	reg := prometheus.NewRegistry()
	app := worker.New(cfg, log, reg, clock.Real{}, rand.New(rand.NewPCG(seed1, seed2)))

	g, gctx := errgroup.WithContext(ctx)
	g.Go(func() error { return app.Scheduler(gctx) })
	g.Go(func() error { return app.ConfigSync(gctx) })
	g.Go(func() error { return app.ServeInternal(gctx, reg) }) // health + metrics listener
	err = g.Wait()

	stop() // a second signal now kills a hung shutdown
	shutdownErr := app.Shutdown(context.Background(), cfg.Shutdown)
	if errors.Is(err, context.Canceled) {
		err = nil
	}
	return errors.Join(err, shutdownErr)
}
```

`run` takes its inputs as parameters, so tests call it with a fake environment and a buffer.

## Config loader

- One struct, one `Load(args, getenv)` that returns `(Config, error)`.
- Parse every value with the strict parser (`strconv.Atoi`, `time.ParseDuration`) and return
  `fmt.Errorf("%s: %w", key, err)` on failure.
- Range checks after parsing: durations `> 0`, ports `1..65535`, worker counts `>= 1` and below a documented cap.
- File config: `yaml.Decoder.KnownFields(true)` or `json.Decoder.DisallowUnknownFields()`.
- Live reload, if supported: a failed reload logs an error and keeps the running config. It never exits.

Table test shape:

```go
cases := map[string]struct{ env map[string]string; wantKey string }{
	"negative interval": {map[string]string{"CHECK_INTERVAL": "-5s"}, "CHECK_INTERVAL"},
	"not a number":      {map[string]string{"WORKERS": "abc"}, "WORKERS"},
	"missing endpoint":  {map[string]string{"CONTROL_URL": ""}, "CONTROL_URL"},
}
```

## Ordered shutdown

| Step | Action | Own timeout |
|---|---|---|
| 1 | readiness returns 503 (draining); refuse new jobs | none |
| 2 | wait for the load balancer to stop routing | drain delay |
| 3 | `srv.Shutdown(ctx)` on public listeners | listener budget |
| 4 | wait for in-flight jobs (`pool.Wait` with deadline) | work budget |
| 5 | flush producer, then wait for async delivery callbacks, then close the fallback buffer | flush budget |
| 6 | close clients, deregister from the control plane (best effort, bounded) | close budget |

The orchestrator's grace period is larger than the sum. Async delivery callbacks that write to a fallback buffer
must finish before that buffer closes: track them with a `sync.WaitGroup` and wait with a bound.

## Bounded pool with shedding

```go
g := new(errgroup.Group)
g.SetLimit(cfg.Workers)
for job := range due {
	if !g.TryGo(func() error { return runJob(ctx, job) }) {
		metrics.Shed.Inc() // the schedule keeps its timing; the job runs next tick
	}
}
```

Callers that can wait (backfill, replay) use `g.Go`, which blocks when the limit is reached.

## Retry with full jitter

```go
func backoff(attempt int, base, max time.Duration, r *rand.Rand) time.Duration {
	ceil := base << attempt
	if ceil <= 0 || ceil > max { // overflow or above cap
		ceil = max
	}
	return time.Duration(r.Int64N(int64(ceil) + 1))
}
```

Status handling for a client of a control plane:

| Response | Action |
|---|---|
| 2xx | success, reset the failure counter |
| 429, 503 | retry after `Retry-After` if present, else backoff |
| other 5xx, transport error | retry only if the method is idempotent or carries an idempotency key |
| 400, 413, 422 | drop the batch as poison, count it, emit an event |
| 401, 403 | back off with a long floor; re-register only after N consecutive failures |

## Atomic credential write

```go
func writeFileAtomic(dir, name string, data []byte) error {
	f, err := os.CreateTemp(dir, "."+name+".tmp-*")
	if err != nil {
		return err
	}
	tmp := f.Name()
	defer os.Remove(tmp) // no-op after a successful rename
	if err := f.Chmod(0o600); err != nil {
		f.Close()
		return err
	}
	if _, err := f.Write(data); err != nil {
		f.Close()
		return err
	}
	if err := f.Sync(); err != nil {
		f.Close()
		return err
	}
	if err := f.Close(); err != nil {
		return err
	}
	if err := os.Rename(tmp, filepath.Join(dir, name)); err != nil {
		return err
	}
	d, err := os.Open(dir)
	if err != nil {
		return err
	}
	defer d.Close()
	return d.Sync()
}
```

The temp file is created in the target directory so the rename never crosses a filesystem.
