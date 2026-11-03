# Content depth, product truth and comparison pages

## Depth

- Compare against what ranks for the query today, element by element, not by length. Google has no preferred
  word count.
- Elements a template cannot produce: screenshots of the real product, numbers read from the product's config
  or data, a migration guide with real steps, a dated price table, limits per plan, a worked example from an
  actual setup, the author's first-hand result.
- Programmatic pages (per city, industry, integration, competitor pair) only when each page receives data that
  exists for that page alone. Otherwise one overview page and 301s. No new variants while the existing ones do
  not rank.
- Do not change a page's date without a substantive change.
- AI-written drafts get a manual fact check, including title, description, structured data and alt text.

Sources: https://developers.google.com/search/docs/fundamentals/creating-helpful-content,
https://developers.google.com/search/docs/essentials/spam-policies,
https://developers.google.com/search/docs/fundamentals/using-gen-ai-content (verified 2026-11-03).

## Product-truth table

Before a page ships, one row per claim:

| Claim on page | Source of truth | Checked on |
|---|---|---|
| "Checks every 30 seconds on the Team plan" | `config/plans.php` line 42 | 2026-11-03 |
| "Exports to CSV and JSON" | `src/Export/Formats.php`, test `ExportFormatsTest` | 2026-11-03 |

- The source is code, config, a spec of shipped behaviour or a dated measurement. Another marketing page, a
  changelog draft or a roadmap is not.
- A claim without a row is cut. A planned feature is not written.
- Shipped differentiators that no page mentions are findings too: compare the feature list in code with the
  pages.
- Claims law (UWG §§ 5, 6) and the claims file: `eu-de-legal-baseline`. Wording: `human-copy`.

## Comparison and alternative pages

Anatomy:

1. Who this comparison is for, in one sentence.
2. A table of like-for-like facts. Every competitor fact has a source URL and the date it was read; facts come
   from `market-analysis` where one exists.
3. What the competitor does better, stated plainly, and who should choose it.
4. Where your product differs, each point backed by the product-truth table.
5. Migration: what moves, what does not, how long it takes, with steps that were tried.
6. Re-check date and a correction contact.

Rules:

- No disparaging wording, no "beats X on everything", no claims about a competitor that cannot be verified.
- One page per competitor that buyers actually search for, not one per pair.
- Re-check competitor facts at the stated date; an expired table is updated or removed.
- In Germany comparative advertising must meet UWG § 6 (same need, objective, verifiable, typical features or
  price, no confusion, no disparagement). Route the draft through `eu-de-legal-baseline` for lawyer review.

Source: https://www.gesetze-im-internet.de/uwg_2004/__6.html (verified 2026-11-03).
