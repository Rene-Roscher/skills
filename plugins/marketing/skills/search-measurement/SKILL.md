---
name: search-measurement
description: "Measures search and site performance live through the Google Search Console, Bing Webmaster and Plausible APIs with read-only keys, stores dated snapshots and runs the measure, change, re-measure loop: baseline, change log, lag-safe equal windows, control group, sign-up attribution. Use when asked for clicks, rankings, traffic or whether a site change worked. Not for on-page fixes (search-visibility)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Search measurement

This skill reads what search engines and the site's analytics report, through their official APIs, and turns
it into dated evidence: a baseline before a change, a logged hypothesis, and a re-measurement that either
shows an effect against a control group or leads to a revert. It also checks the measuring tools themselves,
because a dropped UTM parameter or a bot wave looks exactly like a real trend. It does not decide what to
change on a page (`search-visibility`), which channels to invest in (`go-to-market`), or how titles read
(`human-copy`); it tells those skills what moved and whether a change earned its keep.

## Applies when / does not apply

- Applies: "how is the site doing in search", clicks, impressions, CTR, positions, indexing state, "did the new
  titles work", traffic by landing page or channel, setting up API access, a baseline before a site change, a
  re-measurement date in the change log, "which channel brings paying customers".
- Does not apply: fixing canonicals, hreflang, structured data or content (`search-visibility`); launch, channel
  and outreach plans (`go-to-market`); writing the new title (`human-copy`); product analytics inside the app.

## Rules

Examples use a booking system for venues and an invoicing app.

### Access and evidence

- [invariant] Every number comes from an API call or an export made this session, stated with source, window,
  data state and filter. With no access (`measure.py` exit 3), the answer is "not measured", followed by what the
  owner must set up; nothing is estimated from memory or third-party tools. Why: a remembered position reads as
  precise as a measured one and decides the same work. Test: without credentials, `measure.py gsc` exits 3 and
  the reply names no click or position figure. Source:
  https://developers.google.com/webmaster-tools/v1/searchanalytics/query (verified 2026-11-03).
- [invariant] Keys and tokens live in environment variables or in mode-600 files outside the repository
  (default `~/.config/search-measurement/`). They never go into chat, command arguments, logs, snapshots or
  commits. A key pasted into chat is treated as exposed: do not use or repeat it, ask the owner to rotate it
  and store the new one in the file. Why: a transcript, a shell history and a git history all outlive the
  session. Test: `measure.py --self-test` refuses a mode-644 key file, a key inside a git work tree, and a
  snapshot that would contain a registered secret, and redacts keys from error text. Source:
  https://docs.cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys (verified 2026-11-03).
- [invariant] Least privilege: the Google service account gets the `webmasters.readonly` scope and a Restricted
  user on the property; Plausible gets a "Stats API" key, not a Sites API key; the Bing key belongs to one user
  and covers all of that user's sites, so use a dedicated account when that reach is too wide. Why: these
  credentials sit on a laptop and in scripts. Test: the JWT built by the script carries only the read-only
  scope (self-test). Source: https://support.google.com/webmasters/answer/7687615,
  https://plausible.io/docs/stats-api, https://learn.microsoft.com/en-us/bingwebmaster/getting-access
  (verified 2026-11-03).
- [invariant] Search Console windows end at least 3 days before today in Pacific Time and use
  `dataState=final`; compared windows have equal length in whole weeks, and seasonality is checked against the
  same weeks a year earlier. Why: data is "typically available after 2-3 days", dates are Pacific Time, and
  weekday mix moves B2B traffic. Test: `measure.py window --days 28` ends 3 days ago and gives previous and
  year-ago windows that start on the same weekday. Source:
  https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data and
  https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops (verified 2026-11-03).

### The loop

- [invariant] No change ships without a baseline snapshot and a change-log entry written first: date, page set,
  control set, hypothesis, expected metric with direction and size, re-measure date, revert condition. Why:
  after the change, "before" can only be reconstructed from data that already mixes in the change. Test: the
  entry exists in `docs/growth/changes.md` and a snapshot dated before the go-live date is in
  `docs/growth/snapshots/`. Source: https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops
  ("wait a few weeks" before evaluating) (verified 2026-11-03). Template:
  [assets/changes.md](assets/changes.md).
- [invariant] The clock starts when Google has recrawled the changed pages, not at the commit: confirm the
  deployed HTML carries the change, then URL Inspection `lastCrawlTime` after the go-live date; re-measure no
  earlier than 28 days of final data after that. Why: an undeployed or uncrawled change measures nothing.
  Test: `measure.py inspect` on the page set shows `lastCrawlTime` later than the logged date. Source:
  https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult (verified 2026-11-03).
- [invariant] Never claim an effect from one week, from average position alone, or without a control group.
  `measure.py compare` with `--treated` and `--control` must report `claimable: true`; the effect is the
  difference in differences, and position is read per query. Why: average position averages each query's
  topmost position over impressions, so new low-ranking queries make it worse while every ranking improves.
  Test: the self-test fixture shows position 6.0 to 7.6 overall and 6.0 to 5.0 on the same queries, flagged
  `position_mix_shift`, and blocks a 7-day window. Source: https://support.google.com/webmasters/answer/7042828
  (verified 2026-11-03).
- [default] The control group is a set of comparable pages nobody touches during the window: same template or
  page type, similar impressions, same market, chosen and logged before the change. Trade-off: fewer pages can be
  changed at once. Deviate only with an ADR that names this trade-off. Source: reproducible with
  `measure.py --self-test` (the claim gates and difference in differences).
- [default] One change type per page set per window, and items under 100 impressions per window count as
  "insufficient data"; small pages are judged as a group. Trade-off: slower learning on small sites. Deviate
  only with an ADR that names this trade-off. Source:
  https://developers.google.com/search/blog/2022/10/performance-data-deep-dive (anonymized queries leave rows
  incomplete) (verified 2026-11-03).
- [default] On the re-measure date, a change whose difference in differences is negative or inside the noise is
  reverted, unless it fixes something wrong for users (a broken canonical, a false claim); the outcome is written
  into the change log either way. Trade-off: some changes that would have paid off later are undone. Deviate
  only with an ADR that names this trade-off. Source: reproducible with `measure.py compare`.

### Attribution and tool checks

- [invariant] "Which channel brings paying customers" is answered from the product's own database: the sign-up
  source (UTM parameters, referrer, landing page) is captured at sign-up, stored on the account at creation and
  joined with revenue. Analytics alone cannot tie a visit to a paying customer. Why: privacy-friendly analytics
  keeps no persistent visitor identifier and usually ends where the app domain starts. Test: a query over
  accounts grouped by stored source with revenue returns rows; a reply built from analytics referrals alone says
  it shows visits, not customers. Source: https://plausible.io/data-policy ("does not let us recognize the same
  visitor across days") (verified 2026-11-03).
- [invariant] Check the measuring tools before trusting a trend: a tagged link keeps its UTM parameters through
  every redirect to the final URL, the analytics snippet loads on each template, a jump in direct traffic is
  checked for one country, hostname or 100 % bounce (bots), and the analytics organic trend moves with the
  Search Console click trend. Why: a redirect that drops the query string turns a campaign into "direct". Test:
  `curl -sIL "https://www.example.com/?utm_source=check"` shows `utm_source=check` in the last `location`, or
  the redirect needs fixing. Source: https://plausible.io/docs/stats-api (`visit:source` comes from
  `utm_source`, `source`, `ref` or the Referer header) (verified 2026-11-03).
- [default] AI visibility is read from the Search Console generative AI report and Bing's AI Performance report,
  both UI only, plus assistant referrals in analytics and a fixed panel of buyer questions run on a date with the
  answers saved. The agent asks the owner for a dated export or screenshot of the two reports. Trade-off: manual
  steps every month. Deviate only with an ADR that names this trade-off. Source:
  https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports and
  https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
  (verified 2026-11-03).

## Procedure

1. Access gate: run `python3 ${CLAUDE_SKILL_DIR}/scripts/measure.py window` and one cheap call per source (in
   clients without `CLAUDE_SKILL_DIR`, the script is in this skill's `scripts/` folder). Exit 3: say what is not
   measured and hand the owner the setup steps from [references/credentials.md](references/credentials.md).
2. Tool check: redirects keep UTM parameters, snippet on every template, direct-traffic anomalies, GSC versus
   analytics trend ([references/loop.md](references/loop.md)).
3. Baseline: `measure.py snapshot --label baseline --gsc-site ... --bing-site ... --plausible-site ...` writes
   `docs/growth/snapshots/YYYY-MM-DD-baseline.json`. Add URL Inspection for the pages in scope.
4. Readout: findings as URL, measured value, expected value, likely cause, expected effect, sorted by effect per
   effort. Hand page fixes to `search-visibility` and wording to `human-copy`.
5. Before a change ships: write the entry in `docs/growth/changes.md` from [assets/changes.md](assets/changes.md),
   with the treated and control lists as files under `docs/growth/sets/`.
6. After go-live: confirm the served HTML, then `measure.py inspect` until `lastCrawlTime` is past the go-live
   date. Set the re-measure date to that day plus 28 days plus the lag.
7. Re-measure: a new snapshot over an equal window, then
   `measure.py compare BEFORE.json AFTER.json --treated docs/growth/sets/ID-treated.txt --control
   docs/growth/sets/ID-control.txt --change-date YYYY-MM-DD`. Read `claimable`, `blocking`, the difference in
   differences and every `position_mix_shift`.
8. Decide keep, revert or extend; write the outcome and the numbers into the change log.
9. Report: what was measured (source, window, data state), what was not and why, the claim status, next date.

Exit codes: 0 done, 1 check failed, 2 usage, 3 no access (nothing measured), 4 API refused (quota, rate
limit, error). API details and limits: [references/apis.md](references/apis.md).

## Traps

- Summing query rows and calling it the total: anonymized queries are missing from rows and from any filtered
  query, so rows add up to less than the chart.
- Mixing totals from page tables and property tables: by-page aggregation counts one impression per page.
- `dataState=all` or a window ending yesterday: the last days are partial and look like a drop.
- Clicks down with impressions stable: a snippet or results-page problem, not a ranking loss.
- Reading Bing numbers as daily (they update weekly), or sitemap `indexed` counts (deprecated by Google).
- Treating Plausible "Direct" as people typing the URL: assistants that send no referrer land there too.
- A win announced in week one, a change that never deployed, a control page someone edited mid-window.
- Committing snapshots of a public repository: search queries can contain names and client brands.
- A third-party connector holding the Google credential: it reads every property the account sees.

## Done when

- Every figure in the report names source, window, data state and filter, or is marked "not measured".
- A baseline snapshot and a change-log entry with page set, control set, hypothesis and re-measure date exist
  before any change ships.
- Effect claims come only from `compare` with `claimable: true`; otherwise the report says why not yet.
- No key or token appears in chat output, command lines, snapshots or commits.

## References

- [references/apis.md](references/apis.md): load before calling an API or reading its numbers (limits, lag,
  quotas, UI-only reports, verified and unverified facts).
- [references/credentials.md](references/credentials.md): load when access is missing or being set up.
- [references/loop.md](references/loop.md): load for a baseline, a change, a re-measurement or a tool check.
- [assets/changes.md](assets/changes.md): copy to `docs/growth/changes.md`; one entry per change.
- `scripts/measure.py`: subcommands `gsc`, `inspect`, `sitemaps`, `bing`, `plausible`, `snapshot`, `compare`,
  `window`; `--help` per subcommand; `--self-test` runs offline against `scripts/fixtures/`.

## Sources

- Search Console API, verified 2026-11-03:
  https://developers.google.com/webmaster-tools/v1/searchanalytics/query (scopes, `dataState`, Pacific Time),
  https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data (lag, 25,000 rows, paging),
  https://developers.google.com/webmaster-tools/limits (quotas),
  https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult (index status).
- Search Console reading, verified 2026-11-03: https://support.google.com/webmasters/answer/7042828 (average
  position), https://developers.google.com/search/blog/2022/10/performance-data-deep-dive (anonymized queries),
  https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops (waiting, year over year).
- Access, verified 2026-11-03: https://developers.google.com/identity/protocols/oauth2/service-account,
  https://learn.microsoft.com/en-us/bingwebmaster/getting-access, https://plausible.io/docs/stats-api,
  https://plausible.io/data-policy.
- The claim gates, the position-mix check and the key handling are reproducible with `measure.py --self-test`.
