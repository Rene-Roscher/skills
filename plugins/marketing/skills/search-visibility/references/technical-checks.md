# Technical checks

Checks run per URL or URL group during an audit. Each failed check becomes a finding in the SKILL.md format.
Sources were read on 2026-11-03; the vendor syntax stays in the linked docs.

## Access and status

- Every URL in the sitemap returns 200, is indexable (no `noindex` in HTML or the `X-Robots-Tag` header) and its
  canonical points to itself. A sitemap entry that redirects, 404s or canonicalises elsewhere is a finding.
- Fetch with JavaScript disabled. The `<title>`, the single `<h1>`, the body text and every FAQ or accordion
  answer are present in the HTML. A `noindex` added by JavaScript has undefined behaviour in Google; set it on
  the server. Source: https://developers.google.com/search/updates (2025-12-15 entry) (verified 2026-11-03).
- robots.txt and the CDN or WAF bot rules are read together. A bot challenge for a user agent the robots.txt
  allows is a finding.
- Host and path variants: `http`, `www`, the bare domain, trailing slash, upper case. Exactly one answers 200;
  the rest redirect in one hop.
- Retired hosts and sections redirect to the closest live page. Error status codes on a host that still gets
  impressions send searchers nowhere.
- Behind a TLS-terminating proxy, check that redirects keep `https`; some web servers build absolute redirects
  from the scheme they see.

## Canonical

- Redirects and `rel=canonical` are strong canonical signals; sitemap inclusion is a weak one; signals stack.
  Use `rel=canonical`, not `noindex`, to choose a canonical within a site.
- A canonical to the home page from a page with its own content removes that page from ranking on its own.
- Parameter variants (tracking, sort, filter) canonicalise to the clean URL.

Source: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (verified
2026-11-03).

## hreflang

- Each version lists itself and every other version; one-way annotations are ignored.
- Codes: ISO 639-1 language, optional ISO 3166-1 alpha-2 region after it; a region alone is invalid.
- `x-default` for visitors whose language matches no version.
- The canonical of each version is in the same language.
- Two language versions that say the same thing compete in markets where both are readable. Order of fixes:
  regional codes, real differences in content (local prices, examples, legal notes), then removal from the
  sitemap and internal links. Never `noindex` a member.

Source: https://developers.google.com/search/docs/specialty/international/localized-versions (verified
2026-11-03).

## Titles and snippets

- One `<title>` and one meta description per URL, unique across the site, describing the page's single intent.
- Clicks falling while impressions stay flat points at the snippet or a changed results page, not at ranking.
  Rewrite title and description, then re-measure via `search-measurement`.

## Structured data

Still shown as rich results or used for the entity (Google search gallery, verified 2026-11-03): Article,
Breadcrumb, Organization, Product (with Offer), Software app, Video, Profile page, Review snippet, Event, Q&A,
Discussion forum and others. Not shown: FAQ (from 7 May 2026), HowTo (from 13 September 2023).

- Markup matches visible text. Generated markup gets the same fact check as the page.
- Existing `FAQPage` markup does no harm; do not add or extend it for a search result.
- Review stars: ineligible when the reviewed entity controls the reviews about itself, including embedded
  third-party widgets; never aggregate ratings from other sites; incentivised reviews must be disclosed.
- Validate with the vendor's rich-result test before relying on a feature.

Sources: https://developers.google.com/search/docs/appearance/structured-data/search-gallery,
https://developers.google.com/search/docs/appearance/structured-data/review-snippet,
https://developers.google.com/search/docs/fundamentals/using-gen-ai-content (verified 2026-11-03).

## Core Web Vitals

- Good at the 75th percentile of page loads, mobile and desktop separately: LCP 2.5 s or less, INP 200 ms or
  less, CLS 0.1 or less. INP is the successor to FID (https://web.dev/articles/inp).
- Field data (CrUX, real-user monitoring) decides; lab runs explain why. A page without enough field data has
  no CWV verdict.

Source: https://web.dev/articles/vitals (verified 2026-11-03).
