# The measure, change, re-measure loop

## Contents

- Files in the project
- Baseline
- Readout and levers
- Before a change ships
- After go-live
- Re-measure and decide
- Reading the numbers
- Attribution to revenue
- Checking the measuring tools
- AI visibility panel


Load this for a baseline, a planned change, a re-measurement or a check of the measuring tools.

## Files in the project

```
docs/growth/
  changes.md                    change log, one entry per change (template: assets/changes.md)
  sets/CH-007-treated.txt       pages (or queries) changed, one per line
  sets/CH-007-control.txt       comparable pages nobody touches during the window
  snapshots/2026-09-02-baseline.json
  snapshots/2026-11-05-ch-007-after.json
```

Search queries can contain personal names and client brands. In a public repository, gitignore `snapshots/` and
keep them in private storage; the change log holds the summary numbers.

## Baseline

- Before the first change, and again whenever the last snapshot is more than 7 days older than a planned
  go-live: `measure.py snapshot --label baseline` with every source that has access.
- Default window 28 days ending 3 days ago (Pacific Time). Run `measure.py window` to see it with its previous
  and year-ago windows.
- For pages in scope, add `measure.py inspect --urls-file docs/growth/sets/[id]-treated.txt` to record index
  state, `lastCrawlTime` and the canonical Google chose.
- Pull the year-ago window once with `measure.py gsc --start ... --end ...` to know the season before reading
  any trend; Google's traffic-drop guide recommends the last 16 months and a year-over-year view
  (https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops, verified 2026-11-03).

## Readout and levers

Findings take one form: URL, measured value with window, expected value, likely cause, expected effect, sorted
by effect per effort. Patterns that usually pay off first (practice, not vendor rules):
- Queries with impressions at positions 5 to 20 for a page that fits the query.
- Top-10 positions with a CTR well below the site's own CTR at that position: a title or description problem.
- The home page ranking for a query a specific page targets: the specific page is thin or weakly linked.
- Pages in the sitemap with `verdict` `NEUTRAL` or `FAIL`, or a Google canonical that differs from the declared
  one: indexing comes before content.
- Positions split by country; one aggregate position hides the market that matters.

The fixes themselves belong to `search-visibility`; wording to `human-copy`.

## Before a change ships

1. Write the change-log entry from `assets/changes.md`: id, hypothesis in one sentence, change type, treated
   file, control file, primary metric with direction and minimum size, window, re-measure date, revert
   condition, baseline snapshot path.
2. Choose the control set at the same time: same template or page type, similar impression band (within a factor
   of about 2), same country mix, not linked from the changed pages more than before. Ten or more pages when the
   site has them; otherwise the readout is "directional only".
3. One change type per treated set per window. A title rewrite and a content expansion on the same pages give one
   number for two causes.
4. Note external events in the change log as they happen: search engine core updates, deploy outages, tracking
   changes, campaigns, seasonal peaks.

## After go-live

- Confirm the change is served: fetch the live HTML of two or three treated pages and check the changed element.
  A build that silently did not deploy is the most common reason for "no effect".
- Run `measure.py inspect` on the treated set every few days until `lastCrawlTime` is after the go-live date for
  most pages. The recrawl date, not the commit date, is the start of the effect window.
- Re-measure date: recrawl date plus 28 days plus 3 days of lag. Write it into the entry.

## Re-measure and decide

```
measure.py snapshot --label ch-007-after --gsc-site sc-domain:example.com --start A --end B
measure.py compare docs/growth/snapshots/[baseline].json docs/growth/snapshots/[after].json \
  --treated docs/growth/sets/CH-007-treated.txt --control docs/growth/sets/CH-007-control.txt \
  --change-date [recrawl date]
```

- The before window has the same length as the after window and lies wholly before the change; the after window
  starts at or after the recrawl. Both whole weeks.
- `claimable: false` lists its reasons in `blocking`. Do not report an effect until they are gone; report
  "too early" with the date when they will be.
- With `claimable: true`, report the difference in differences for clicks and impressions, the treated and
  control percentages, and any page flagged `position_mix_shift` with its same-query position.
- Decide: keep (effect in the expected direction and above the minimum size), revert (negative or within
  noise, and the change was not a correctness fix), extend (directional, small sample: one more window, same
  sets). Write the outcome with the numbers into the entry.

## Reading the numbers

- Average position is each query's topmost position averaged over the queries
  (https://support.google.com/webmasters/answer/7042828, verified 2026-11-03). New impressions at low positions
  raise it while every ranking improves. Read per query, or the same-query figure `compare` prints.
- Impressions up with clicks flat often means new low-position queries, not a CTR problem.
- Impressions stable with clicks down points at the snippet or the results page (rich results, AI features), per
  the traffic-drop guide.
- Items under 100 impressions per window swing on a handful of searches; `compare` marks them
  `insufficient_data`. Judge small pages as a group.
- Row sums are smaller than totals because anonymized queries have no rows; filtered queries drop them entirely.
- GSC clicks and analytics visits never match (consent, blockers, redirects, the domain change to the app).
  Compare their trends, not their levels.
- Bing figures update weekly; a 28-day Bing window covers about four data points.

## Attribution to revenue

The answer to "which channel brings paying customers" lives in the product database:
1. On the marketing site, the sign-up link carries the visit's source: `utm_source`, `utm_medium`,
   `utm_campaign` from the landing URL, the first-party referrer, and the landing path.
2. The app stores these on the account (or organization) when it is created, once, never overwritten by later
   visits.
3. Revenue per account comes from billing. A monthly query groups paying accounts and revenue by stored source.
4. Analytics shows visits and sign-up clicks per source; it cannot see payments, and privacy-friendly analytics
   cannot follow a visitor across days. Present it as the top of the funnel only.
Keep analytics events few and uniform (one sign-up click event with a `source` property, not one event per
button) and never put free text in event properties, where personal data leaks into statistics.

## Checking the measuring tools

Run before trusting a trend and after any site, redirect or consent change:
- UTM survival: `curl -sIL "https://www.example.com/?utm_source=check&utm_medium=test"`; the last `location`
  still carries the parameters. A redirect that drops the query string turns campaigns into direct traffic.
- Snippet coverage: the analytics script is in the served HTML of every template (home, pricing, docs, blog,
  sign-up page).
- Bot share: a jump in direct traffic concentrated on one country, one hostname, one entry page, or with near
  100 % bounce and zero duration is bots until shown otherwise; filter it out of the comparison and say so.
- Cross-check: the analytics "Organic Search" trend moves with Search Console clicks over the same window. If
  they diverge, find out why before reading either.
- Deploy check: the change you are measuring, and the analytics snippet, are actually live.
- Script check: `measure.py --self-test` passes before a new snapshot series starts.

## AI visibility panel

AI answers are not in any of the APIs above.
- Ask the owner for the Search Console generative AI report and Bing AI Performance exports for the snapshot
  window (see the table in `references/apis.md`).
- Keep a fixed panel of about 15 questions a buyer would ask before choosing a product in this category, in each
  market language. Run it on a date in each assistant the buyers use, with a clean session, and save the
  answers verbatim with date, assistant and locale. One run is a sample; the trend over months is the signal.
- Assistant referrals in analytics complete the picture; assistants without a referrer are hidden in direct.
