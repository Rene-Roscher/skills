# APIs: endpoints, limits and lag

## Contents

- Labels used here
- Google Search Console: Search Analytics
- Google Search Console: URL Inspection and sitemaps
- Google sign-in for scripts
- Bing Webmaster Tools
- Plausible Stats API v2
- Reports that exist only in a UI
- What `measure.py` sends and stores


Read this before calling an API or interpreting what it returns. Request syntax lives in the vendor docs;
this file keeps the limits, the lag and the traps. Every line was read on the linked page on 2026-11-03
unless it says "unverified". Check the vendor page again when a call fails in a way this file does not explain.

## Labels used here

- verified 2026-11-03: read on the vendor's own documentation page on that date.
- unverified: believed from practice or third-party reports, not found on a vendor page. Say so when you rely on it.

## Google Search Console: Search Analytics

Source: https://developers.google.com/webmaster-tools/v1/searchanalytics/query,
https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data,
https://developers.google.com/webmaster-tools/limits,
https://developers.google.com/search/blog/2022/10/performance-data-deep-dive (verified 2026-11-03).

- `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`. `siteUrl` is a URL-prefix
  property (`https://www.example.com/`) or a domain property (`sc-domain:example.com`), URL-encoded in the path.
- Scopes: `webmasters.readonly` is enough for reading.
- Dimensions: `query`, `page`, `country`, `device`, `searchAppearance`, `date`, `hour`. Search types: `web`
  (default), `image`, `video`, `news`, `discover`, `googleNews`. Filter operators: `contains`, `equals`,
  `notContains`, `notEquals`, `includingRegex`, `excludingRegex`.
- `rowLimit` 1 to 25,000; page with `startRow` until a response has 0 rows. The API exposes at most 50,000 rows
  per day per site per search type, sorted by clicks. Default without `rowLimit` is 1,000 rows.
- `dataState`: `final` (default, finalized only), `all` (includes fresh, possibly incomplete data), `hourly_all`
  (with the `hour` dimension).
- Lag: data is "typically available after 2-3 days". `startDate` and `endDate` are in Pacific Time.
- Rows carry `keys`, `clicks`, `impressions`, `ctr` (0 to 1), `position`. `responseAggregationType` says whether
  the result was aggregated by page or by property; grouping or filtering by page forces by-page.
- Anonymized queries ("not issued by more than a few dozen users over a two-to-three month period") never appear
  as rows; they are in chart totals unless a query filter is set, and any filter drops them.
- Quotas: Search Analytics 1,200 queries per minute per site and per user, 40,000 per minute and 30,000,000 per day
  per project. Grouping or filtering by page and query together is the most expensive request type, so a
  page-by-query pull over a long range is the one to schedule sparingly.
- History: 16 months (from the traffic-drop guide, which recommends looking at the last 16 months).

## Google Search Console: URL Inspection and sitemaps

Source: https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect,
https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult,
https://developers.google.com/webmaster-tools/v1/sitemaps (verified 2026-11-03).

- `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect` with `inspectionUrl` and `siteUrl`.
  The URL must belong to the property. It reports the version in the Google index only: no live test and no
  request-indexing method.
- Quota: 2,000 per day and 600 per minute per site. `measure.py inspect` paces requests, caps a run with `--max`
  (default 100) and keeps a per-site, per-Pacific-day count in `~/.cache/search-measurement/inspect-usage.json`.
  The count covers only calls made by this script.
- Useful fields: `verdict` (`PASS` valid, `NEUTRAL` excluded, `FAIL` error), `coverageState`, `indexingState`,
  `robotsTxtState`, `pageFetchState`, `lastCrawlTime` (RFC 3339, UTC; absent when never crawled),
  `googleCanonical` (absent when not indexed), `userCanonical`, `crawledAs`. The script flags
  `canonical_mismatch` when Google chose a different canonical than the page declares.
- Sitemaps: `GET .../sites/{siteUrl}/sitemaps`. `contents[].indexed` is marked "Deprecated; do not use."; read
  indexing from URL Inspection or the page indexing report instead.

## Google sign-in for scripts

Source: https://developers.google.com/identity/protocols/oauth2/service-account (verified 2026-11-03).

- Service account: a JWT with header `alg` `RS256`, claims `iss` (service-account email), `scope`
  (space-separated), `aud` `https://oauth2.googleapis.com/token`, `iat`, `exp` at most one hour after `iat`,
  signed with the account's private key and exchanged at `https://oauth2.googleapis.com/token` with
  `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`.
- `measure.py` builds the JWT in Python and signs it with `openssl dgst -sha256 -sign`, passing the key through
  a pipe so it never touches disk or the process list. Without `openssl`, set `GSC_ACCESS_TOKEN` to a token
  obtained another way (for example a user OAuth flow with the read-only scope).
- Adding the service-account email as a user on the property is done in Search Console under Settings, Users and
  permissions, by an owner. Google's API pages do not spell out this step (unverified as a documented
  procedure; standard practice).

## Bing Webmaster Tools

Source: https://learn.microsoft.com/en-us/bingwebmaster/getting-access,
https://learn.microsoft.com/en-us/bingwebmaster/getting-started,
https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi.getquerystats?view=bing-webmaster-dotnet,
https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi.getpagestats?view=bing-webmaster-dotnet
(verified 2026-11-03).

- Auth: OAuth 2.0 (recommended by Microsoft) or one API key per user, generated under Settings, API Access. The
  key is "generated for a user and not a site", so it reaches all of that user's verified sites.
- JSON: `GET https://ssl.bing.com/webmaster/api.svc/json/{Method}?siteUrl=...&apikey=...`. Responses wrap the
  result in `{"d": ...}`; dates look like `/Date(1316156400000-0700)/` (milliseconds and offset). Errors come back
  as HTTP 400 with `{"ErrorCode":3,"Message":"InvalidApiKey"}` and similar.
- `GetQueryStats` and `GetPageStats` return rows with `Query` (the page URL for page stats), `Date`,
  `Impressions`, `Clicks`, `AvgImpressionPosition`, `AvgClickPosition`. "The data will be updated every week."
- The key travels in the query string. The script never logs URLs and redacts `apikey=` from any error text.
- Not wrapped by the script (method names exist in the interface list, parameters unverified):
  `GetPageQueryStats`, `GetQueryPageStats`, `GetKeyword`, `GetCrawlStats`, `GetUrlSubmissionQuota`.

## Plausible Stats API v2

Source: https://plausible.io/docs/stats-api, https://plausible.io/data-policy (verified 2026-11-03).

- `POST https://plausible.io/api/v2/query` (or the self-hosted base URL), `Authorization: Bearer [key]`.
- Plan: "Stats API is a Business plan feature." on Plausible Cloud. For self-hosted Community Edition, check the
  instance (unverified here).
- Keys: "API keys are scoped to one team"; choose the "Stats API" key type. A Stats API key can also read the
  Sites API, but cannot change sites.
- Rate limit: "600 requests per hour by default"; HTTP 429 above it.
- Body: `site_id`, `metrics`, `date_range` (shorthand like `28d` or an ISO pair), optional `dimensions`,
  `filters`, `order_by`, `include`, `pagination` (`limit`, `offset`; default limit 10,000).
- Results: rows with `dimensions` and `metrics` arrays in request order; the script maps them to named fields.
- `visit:source` comes from `utm_source`, `source` or `ref` on the entry URL, or the Referer header.
  `visit:utm_*` are raw values from the entry page. Session metrics (`bounce_rate`, `visit_duration`,
  `views_per_visit`) cannot be mixed with most event dimensions.
- Visitors are counted with a daily rotating hash; Plausible "does not let us recognize the same visitor across
  days". Repeat visits over weeks and the path to payment are therefore not in Plausible.
- An "AI Assistants" acquisition channel is reported in Plausible's source and blog (unverified on the API
  docs page); assistants that send no referrer count as direct.

## Reports that exist only in a UI

| Report | What it shows | API | Ask the owner for |
|---|---|---|---|
| Search Console generative AI performance | impressions in AI Overviews, AI Mode and Discover AI features, by page, country, device, date; no clicks | none mentioned | CSV export or screenshot, with property and date range, same window as the snapshot |
| Bing AI Performance (public preview) | citations, average cited pages, grounding queries (a sample), page-level citations | none mentioned | export or screenshot of citations by page and the grounding queries for the window |
| Search Console custom annotations | notes on the performance chart | not documented (unverified) | nothing; the change log in the repo is the record |

Sources: https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports,
https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
(verified 2026-11-03), https://developers.google.com/search/blog/2025/11/custom-chart-annotations (from the
research notes, not re-read).

Store an export next to the snapshot as `docs/growth/snapshots/YYYY-MM-DD-[report].csv` and name it in the
report. A screenshot is evidence for one date, not a series.

## What `measure.py` sends and stores

- Sends: the request bodies above, with the credential only in the `Authorization` header (Google, Plausible) or
  the `apikey` query parameter (Bing).
- Prints: JSON results on stdout; errors as one JSON line on stderr, redacted, without a traceback.
- Stores: snapshots under `--out` (default `docs/growth/snapshots/`), refusing to write any file that contains a
  credential it has read; the URL Inspection usage count under `~/.cache/search-measurement/`.
- Snapshot layout: `meta` (label, created_at, window, data_state, skipped sources) and `sources.gsc.page`,
  `.query`, `.page_query`, `sources.bing.page`, `.query`, `sources.plausible.entry_page`, `.channel`,
  `.utm_source`, `.goals`, each with the exact request parameters.
