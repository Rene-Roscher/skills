# Changelog

All notable changes to the `business` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `product-strategy`, `pricing-and-unit-economics`, `human-copy`.
- Dependency on `core`.
- Skill `market-analysis` with a template and a checker.
- `human-copy`: voice files that learn from owner corrections, few-shot from approved texts, a separate native-language pass, corpus-backed calque checks with `collocation_check.py`, per-surface rules for UI and transactional mail, and du as the German default.
- `human-copy`: the writer adds no Unicode emoji or pictographic symbol anywhere in a text; `copy_lint.py` EMO01
  now reports them anywhere in a line, not only at its start.
