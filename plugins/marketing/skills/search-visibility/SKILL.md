---
name: search-visibility
description: "Decides technical, on-page and AI-search visibility for marketing and docs sites: indexing, one intent per URL, canonical and hreflang, depth from product facts, honest comparison pages, structured data that still works, AI crawler policy and SEO myths to refuse. Use when auditing SEO, planning a page, or asked why a site does not rank or appear in AI answers. Not for metric pulls or copy tone."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Search visibility

This skill decides what makes a public marketing or docs site findable in search engines and AI assistants,
and what an audit of it reports. It covers crawl and index access, which URL owns which search intent,
canonical and hreflang clusters, content depth, product-truth and comparison pages, structured data, AI crawler
policy and the claims about SEO that have no source. Numbers come from `search-measurement`; copy quality from
`human-copy`; claims law from `eu-de-legal-baseline`. The failure it prevents: pages written for a word count or
a schema type while the real problem is indexing, a second URL competing for the same query, or a claim the
product does not back. Any model running an audit starts with the fast path under Procedure.

## Applies when / does not apply

- Applies: an SEO or "AI visibility" audit; planning, merging or deleting a marketing, docs, comparison or
  alternative page; robots.txt, sitemaps, redirects, canonical, hreflang or structured data; "why don't we
  rank", "why doesn't ChatGPT mention us"; requests to add FAQ schema, `llms.txt` or AI-specific markup.
- Does not apply: pulling Search Console, Bing or analytics data, baselines, change logs and attribution
  (`search-measurement`); tone and wording (`human-copy`); positioning and buyer (`product-strategy`); launch,
  directories, outreach (`go-to-market`); rendering choice for the site (`web-architecture`); visual design
  (`design-quality`).

## Rules

- [invariant] Fix access before content. A URL that should rank returns 200 with its main content (headline,
  body, every FAQ answer) in the server HTML, is not blocked by robots.txt, a CDN or WAF bot rule or `noindex`,
  and is indexed. Moved or retired URLs answer one 301 or 308 hop to the closest equivalent, never 5xx, a soft
  404 or `<meta http-equiv="refresh">`; one host and one trailing-slash form answer 200. Why: only indexed,
  snippet-eligible pages appear in Search and its AI features, and AI crawlers are not documented to run
  JavaScript (Unverified either way). Test: fetch each target URL without JavaScript and find the main text;
  inspection via `search-measurement` says indexed; every old URL resolves in one hop to a 200. Source:
  https://developers.google.com/search/docs/appearance/ai-features,
  https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (verified 2026-11-03).
- [invariant] One primary search intent per URL, and one URL per intent across every owned site, subdomain and
  language version. Before creating a page, name its intent, list the owned URLs that already get impressions
  for it, and extend the best one instead of adding a second. Why: duplicates for one intent split signals and
  Google selects one canonical, not necessarily yours. Test: a page plan names the intent and the URLs checked;
  two owned URLs sharing impressions for one query produce a finding (merge with 301, or differentiate).
  Source: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (verified
  2026-11-03).
- [invariant] Canonicals are self-referencing unless the page is a named duplicate, and never point distinct
  content at the home page. hreflang clusters are reciprocal, each version lists itself, codes are ISO 639-1
  plus optional ISO 3166-1 region, `x-default` covers the rest, and the canonical stays in the same language.
  Never `noindex` a cluster member; fix interchangeable language versions with regional codes, then real
  differences, then sitemap removal and unlinking. Why: one-way hreflang is ignored, and `noindex` blocks the
  page from Search entirely. Test: a crawl of every indexable URL finds canonical equal to itself or a documented
  target, and every hreflang target returns 200 and links back. Source:
  https://developers.google.com/search/docs/specialty/international/localized-versions,
  https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (verified 2026-11-03).
- [invariant] Depth comes from elements only this product can show: product data, screenshots, limits and prices
  read from config, migration steps, measured results. No word-count targets, no fake freshness dates, no
  template pages that differ in a few fields; the data a template receives caps how unique its pages can be.
  Why: Google says it has no preferred word count and names many pages without added value as scaled content
  abuse. Test: for two sibling pages, list what is unique to each; names and a few fields only means merge and
  301. Source: https://developers.google.com/search/docs/fundamentals/creating-helpful-content,
  https://developers.google.com/search/docs/essentials/spam-policies (verified 2026-11-03).
- [invariant] Every product claim on a page (feature, limit, price, integration, location, certification,
  number) traces to code, config or spec in the repository, or to a dated record, before it is published.
  Unbuilt features are left out; another marketing page is never the source. Why: snippets and assistants
  quote pages verbatim, and UWG § 5 covers misleading statements to business buyers. Test: a claims table maps
  each claim on the changed page to a file and line or a dated record, and `check_claims.py --page` exits 0;
  claims without an entry are removed.
  Source: https://www.gesetze-im-internet.de/uwg_2004/__5.html,
  https://developers.google.com/search/docs/fundamentals/using-gen-ai-content (verified 2026-11-03).
- [invariant] Comparison and alternative pages compare like with like, date and source every competitor fact,
  name what the competitor does better and who should pick it, carry a re-check date, and go through
  `eu-de-legal-baseline` (UWG § 6) before they go live for a German audience. Why: a one-sided page fails the
  reader at the decision, and § 6 limits comparative advertising. Test: "say we beat X on everything" yields a
  draft with sourced, dated facts, at least one stated competitor strength and a review flag, or a refusal of
  the unsupported claim. Source: https://www.gesetze-im-internet.de/uwg_2004/__6.html (verified 2026-11-03).
- [invariant] Structured data only for features still in Google's search gallery, or to describe the entity
  truthfully, and always matching visible text. No work for FAQ rich results (not shown since 7 May 2026) or
  HowTo (gone since September 2023); no review stars on pages about yourself; no ratings aggregated from other
  sites. Never present schema as required for AI Overviews or AI answers. Test: "add FAQ schema everywhere for
  rich results" gets the dated retirement, no new FAQ markup, and the visible-content alternative. Source:
  https://developers.google.com/search/updates,
  https://developers.google.com/search/blog/2023/08/howto-faq-changes,
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide,
  https://developers.google.com/search/docs/appearance/structured-data/review-snippet (verified 2026-11-03).
- [default] Allow AI search and user-fetch agents; decide training agents once per site in an ADR; check
  robots.txt and CDN or WAF bot rules together. Never block Googlebot to stay out of AI Overviews. Trade-off:
  allowed training agents may use the content for model training. Deviate only with an ADR that names this
  trade-off. Source: https://developers.openai.com/api/docs/bots, https://support.claude.com/en/articles/8896518,
  https://docs.perplexity.ai/guides/bots,
  https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers (verified 2026-11-03).
- [default] Check indexing in Google, Bing and Brave, and notify Bing and other IndexNow members of changes;
  Google does not take IndexNow. Copilot cites pages from Bing; Claude search uses Brave per secondary sources.
  Trade-off: two more indexes to watch. Deviate only with an ADR that names this trade-off. Source:
  https://www.indexnow.org/searchengines.json,
  https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview,
  https://simonwillison.net/2025/Mar/21/anthropic-use-brave/ (secondary) (verified 2026-11-03).
- [default] No `llms.txt` for rankings or citations; add one only to a docs site that coding agents read on
  purpose. Trade-off: if an assistant starts relying on it, you add it then. Deviate only with an ADR that names
  this trade-off. Source: https://developers.google.com/search/updates (2026-06-15 note) (verified 2026-11-03).
- [default] One `Organization` entity with one `@id` across owned sites, `sameAs` to real profiles, and the same
  one-sentence description everywhere; third-party profiles are corrected when the product changes
  (`go-to-market`). Trade-off: every profile becomes something to keep current. Deviate only with an ADR that
  names this trade-off. Source:
  https://developers.google.com/search/docs/appearance/structured-data/organization (verified 2026-11-03).
- [invariant] Core Web Vitals statements use field data (CrUX or real-user monitoring, 75th percentile, mobile
  and desktop separately: LCP 2.5 s, INP 200 ms, CLS 0.1). Lab scores are diagnostics, never proof of passing or
  of a ranking effect. Test: an audit line "LCP fails" names the field source and percentile, or is marked lab
  only. Source: https://web.dev/articles/vitals (verified 2026-11-03).
- [invariant] An SEO or AEO tactic is called effective only with a vendor document or a measurement behind it.
  Claims listed in [references/myths.md](references/myths.md) are refused with their source. Test: "AI answers
  need 40 to 60 word paragraphs" gets "no vendor source supports this" and Google's guidance. Source:
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (verified 2026-11-03).

## Procedure

### Fast path

Run these steps first, in order. The scripts are in this skill's `scripts/` folder (`${CLAUDE_SKILL_DIR}/scripts/`).

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/site_check.py --text --sitemap https://[host]/sitemap.xml` (or URLs;
   for a build: `--root-dir [dir] --base-url https://[host]`; add `--expect-text "[main sentence]"` per page).
2. A non-zero exit means stop and report. Exit 1: blocker or high findings. Exit 2, 3 or 4: nothing was checked.
3. Copy findings from the script output as printed, severity included. Never add or soften one from memory.
4. Page with product claims: fill [assets/claims-table.md](assets/claims-table.md), then run
   `check_claims.py --table [file] --root . --page [page file]`. Exit 1: source or remove the failing rows first.
5. Judgement calls go to the owner: merging pages, a canonical or block that may be deliberate, comparison
   claims, legal review. A bot block an ADR records: re-run with `--accept-block [token]` and cite the ADR.

### Full audit

1. Read the product context (`product-strategy` output) and the site's surface roles: which domain or section
   targets which intents.
2. Access: `site_check.py` over the sitemap and target URLs (status, redirects, noindex, server-HTML text,
   robots.txt per agent). Read CDN or WAF bot rules by hand; the script cannot see them. Get index status and
   query data from `search-measurement`; do not estimate rankings.
3. Intent map: one row per intent with its owning URL; mark duplicates and orphans.
4. Canonical, hreflang, sitemap and structured data: `site_check.py` covers the mechanical checks; the rest per
   [references/technical-checks.md](references/technical-checks.md).
5. Content: depth, product truth (`check_claims.py`) and comparison pages per
   [references/content-and-comparisons.md](references/content-and-comparisons.md).
6. AI discoverability per [references/ai-discoverability.md](references/ai-discoverability.md).
7. Write findings, sorted by effect per effort. Changes to a live site are deploys: show the diff first
   (`safe-actions`). Hand each change to `search-measurement` for its log entry and re-check date.

Finding format, one per issue:

```text
[severity: blocker | high | medium | low] URL or URL group
Evidence: what was measured, where, when (status code, HTML excerpt, inspection result, query data)
Fix: the concrete change
Verify: how and when to check it worked (re-fetch, re-crawl date, metric and window via search-measurement)
```

## Traps

- More pages for a thin topic. Merging near-duplicates and redirecting usually beats adding variants.
- A help article ranking for unrelated queries drags a domain into the wrong topic; check where impressions go.
- A CDN bot-protection rule blocks AI search agents while robots.txt allows them.
- FAQ answers present only in JSON-LD or a client-rendered accordion: not in the server HTML, not quotable.
- A wildcard subdomain handler that also answers `www` or retired hosts with an error page.
- A deploy that silently did not happen; confirm the served HTML before measuring an effect.
- Clicks fall while impressions hold: a snippet or results-page change, not a ranking loss.

## Done when

- Every finding has severity, URL, evidence, fix and a verification step; none rests on memory or a blog.
- `site_check.py` exits 0 on the changed URLs after the deploy, or each remaining blocker or high finding is in
  the report with an owner.
- `check_claims.py` exits 0 for every changed page that makes product claims.
- The intent map has one owning URL per intent, and planned pages name the intent they take from nobody.
- Changed pages pass the product-truth table and, for comparisons, the legal review flag.
- Each shipped change is logged with `search-measurement` and has a re-check date.

## References

- [references/technical-checks.md](references/technical-checks.md): load for crawl, redirect, canonical,
  hreflang, sitemap and structured-data checks.
- [references/content-and-comparisons.md](references/content-and-comparisons.md): load before writing or
  pruning pages, comparison or alternative pages, or programmatic pages.
- [references/ai-discoverability.md](references/ai-discoverability.md): load for AI crawler policy, where
  assistants get results, IndexNow, `llms.txt` and entity consistency.
- [references/myths.md](references/myths.md): load when a request or a source states an SEO or AEO tactic as
  fact.
- [scripts/site_check.py](scripts/site_check.py): run for any audit or before a deploy; `--help` lists inputs and
  exit codes, `--self-test` runs offline against `scripts/fixtures/`.
- [scripts/check_claims.py](scripts/check_claims.py): run on the claims table of every page with product claims;
  `--self-test` runs offline.
- [assets/claims-table.md](assets/claims-table.md): copy next to a page change; one row per product claim.
- Depth on the technical layer: `addyosmani/web-quality-skills` (`seo`, `core-web-vitals`, `performance`,
  `web-quality-audit`), MIT, listed in `stack-bootstrap`'s curated skills; it also treats field data as the
  proof for Core Web Vitals. https://github.com/addyosmani/web-quality-skills (verified 2026-11-03).

## Sources

- https://developers.google.com/search/docs/appearance/ai-features: AI features requirements, verified 2026-11-03.
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide: no special markup, files or
  chunking, verified 2026-11-03.
- https://developers.google.com/search/updates: FAQ rich results end 2026-05-07, `llms.txt` note 2026-06-15,
  verified 2026-11-03.
- https://developers.google.com/search/blog/2023/08/howto-faq-changes: HowTo retired September 2023, verified
  2026-11-03.
- https://developers.google.com/search/docs/appearance/structured-data/search-gallery: features still shown,
  verified 2026-11-03.
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content and
  https://developers.google.com/search/docs/essentials/spam-policies: word count, scaled content, verified
  2026-11-03.
- https://web.dev/articles/vitals: thresholds and field measurement, verified 2026-11-03.
- https://www.rfc-editor.org/rfc/rfc9309: robots.txt group selection, longest match, 5xx as complete disallow,
  as implemented in `site_check.py`, verified 2026-11-04.
- Crawler and index sources: see the rules above and
  [references/ai-discoverability.md](references/ai-discoverability.md).
