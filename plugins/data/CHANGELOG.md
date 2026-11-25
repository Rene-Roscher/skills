# Changelog

All notable changes to the `data` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skill `postgres-production`.
- Dependency on `core`.

### Fixed

- One `postgres-production` eval case had frontmatter the eval runner rejected, so it never ran; the value is
  quoted now.
