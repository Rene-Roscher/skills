# Changelog

All notable changes to the `delivery` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `github-actions-hardening`, `container-images` and `release-supply-chain`.
- Dependency on `core`.
- Skill `local-dev-stack`.
- `container-images`: an image counts as done only after it ran with the production constraints (arguments
  through the entrypoint, tmpfs owned by the runtime user, every documented mode, healthy, scan); no development
  dependencies or REPLs in the runtime image; every long-running process supervised, health-checked and
  kill-tested; an order for fixing base-package scan findings.
- `github-actions-hardening`: explicit updater cooldown of at least 7 days; pins checked to be commit SHAs, not
  annotated tag objects; a rehearsal before the first push of a workflow (local zizmor and actionlint, the job
  graph, the jobs' commands in a clean clone); CI runs selected by the pushed commit's SHA.
- Eval cases `output-built-is-not-done` and `output-watch-run-by-sha`.
