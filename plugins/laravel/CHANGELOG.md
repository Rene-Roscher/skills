# Changelog

All notable changes to the `laravel` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `laravel-architecture` and `laravel-production-runtime`.
- `octane_scan.py` in `laravel-production-runtime`: statics, singletons, controller constructors, flush list
  and tenant middleware checked for state that outlives a request.
- Dependencies on `core` and on `laravel-boost` from `claude-plugins-official`.
- `laravel-production-runtime`: the scheduler runs as `schedule:run` from a real scheduler with a heartbeat,
  never `schedule:work` or a shell loop; starter-kit leftovers are audited against the runtime spec after a
  scaffold and the table set is guarded by a schema test. Eval cases `adversarial-scheduler-shell-loop` and
  `trigger-starter-leftovers`.
- `laravel-architecture`: dashboard widgets are query classes mapped to load modes in a controller that computes
  nothing, cached per tenant and viewer visibility with `Cache::flexible` and a cold-path lock, heavy KPIs read
  from rollups, cost measured cold and warm; reference `dashboard-data.md` and eval
  `output-dashboard-many-kpis`.
