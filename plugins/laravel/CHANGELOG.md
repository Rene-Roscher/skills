# Changelog

All notable changes to the `laravel` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `laravel-architecture` and `laravel-production-runtime`.
- `octane_scan.py` in `laravel-production-runtime`: statics, singletons, controller constructors, flush list
  and tenant middleware checked for state that outlives a request.
- Dependencies on `core` and on `laravel-boost` from `claude-plugins-official`.
