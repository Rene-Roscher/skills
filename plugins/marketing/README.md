# marketing

Search and AI discoverability, live measurement and go-to-market for B2B SaaS. The skills are written for an
agent that works next to a professional: every number comes from an API call made in the session, every SEO
tactic needs a vendor source or a measurement, and every change to a site is logged and measured again
against a control group before anyone calls it a win.

## Skills

| Skill | Use it when |
|---|---|
| `search-visibility` | auditing SEO or AI visibility, planning, merging or deleting a page, robots.txt, redirects, canonical, hreflang, structured data, comparison pages, or asked why a site does not rank or appear in AI answers |
| `search-measurement` | asked for clicks, rankings, indexing or traffic, setting up API access, taking a baseline before a change, re-measuring after one, or asking which channel brings paying customers |
| `go-to-market` | planning a launch, a channel, a campaign, lifecycle mails, outreach or review requests, or choosing between self-serve and sales |

Claude Code loads a skill when the task matches its description. You can call one directly, for example
`/marketing:search-measurement`.

Each skill starts with a short fast path that says which script to run and when to stop, so a smaller model
can follow it without weighing the rules itself. `search-visibility` ships `site_check.py`, which audits live
URLs, a sitemap or a built site without running JavaScript and prints findings in a fixed format, and
`check_claims.py`, which checks that every product claim on a page points to a source line in the repository.
`go-to-market` ships a plan template and `check_gtm_plan.py`, which rejects plans without a cost target per
paying customer, a read date or a legal basis for each outreach row.

`search-measurement` ships `scripts/measure.py`, standard library only, which reads the Google Search Console,
Bing Webmaster and Plausible Stats APIs with read-only keys, writes dated snapshots to `docs/growth/snapshots/`
and compares two windows with a control group. The Google service-account token is signed with the `openssl`
command. Keys stay in environment variables or mode-600 files outside the repository; `references/credentials.md`
in the skill walks through the setup. The Plausible Stats API needs the Business plan on Plausible Cloud.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install marketing@rene-roscher-skills
```

The plugin depends on `core` and `business` from this marketplace, which are installed with it. The skills
refer to `product-strategy`, `pricing-and-unit-economics`, `market-analysis` and `human-copy` from `business`,
to `safe-actions` from `core`, and to `eu-de-legal-baseline` and `gdpr-engineering` from `saas` for claims,
comparisons and outreach law. For depth, `stack-bootstrap` offers `addyosmani/web-quality-skills` and eight
skills from `coreyhaines31/marketingskills`.

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off).

See [CHANGELOG.md](CHANGELOG.md) for changes.
