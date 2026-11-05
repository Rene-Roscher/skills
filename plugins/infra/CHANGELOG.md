# Changelog

All notable changes to the `infra` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skill `high-availability`.
- Skills `infrastructure-as-code`, `kubernetes-workloads`, `edge-proxy-tls` and `observability-and-dr`.
- Dependency on `core`.
- `edge-proxy-tls`: every config edit is validated by the shipped proxy binary (`caddy validate`, `nginx -t`)
  before it is called done, and the edge is started with its production settings before testing.
