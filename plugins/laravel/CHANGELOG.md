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
