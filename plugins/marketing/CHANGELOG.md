# Changelog

All notable changes to the `marketing` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `search-visibility`, `search-measurement` and `go-to-market`.
- Script `measure.py` in `search-measurement` for the Search Console, Bing Webmaster and Plausible Stats APIs,
  snapshots and control-group comparisons, with an offline self-test.
- Dependencies on `core` and `business`.
- Scripts `site_check.py` and `check_claims.py` in `search-visibility`, with a claims table template.
- Plan template and `check_gtm_plan.py` in `go-to-market`, and sales-motion bands from a cited source.
- A fast path at the top of each procedure for smaller models.
