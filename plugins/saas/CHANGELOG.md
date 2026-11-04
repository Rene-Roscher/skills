# Changelog

All notable changes to the `saas` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

- Skills `dual-key-identifiers`, `tenancy-model`, `plan-entitlements`, `tenant-isolation`, `authorization-rbac`, `build-vs-buy`, `billing-eu-b2b`, `gdpr-engineering`, `service-boundaries`, `async-reliability` and `egress-and-webhooks`.
- Skill `localization`: user-facing text through i18n with CLDR plurals, Intl formatting, error codes for
  backend feedback and the recipient's locale, plus `i18n_check.py`.
- Skill `domain-design`: bounded contexts with arch tests, aggregates, domain and integration events, long flows.
- `build-vs-buy` checks reach, bus factor and maintenance with `dep_health.py` and builds small scopes in-house.
- Skill `eu-de-legal-baseline`, including the § 7 UWG rules for advertising by mail, phone and messenger.
