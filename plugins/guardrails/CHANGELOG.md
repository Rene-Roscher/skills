# Changelog

All notable changes to the `guardrails` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Hooks that count failed shell commands per session and agent, report `attempt k/10`, and block edits and
  non-probe commands at the cap until the owner replies; a passing check or an owner message resets the count.
- A block on commands that skip or silence checks: `--no-verify`, `git commit -n`, `core.hooksPath`,
  `HUSKY=0`, `LEFTHOOK=0`, `SKIP=`, and `check || true`.
- An offline `--self-test`.
