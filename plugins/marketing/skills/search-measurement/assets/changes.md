# Growth change log

One entry per change to the public site that is meant to move search or conversion numbers. Newest first.
Write the entry before the change ships; fill in Outcome on the re-measure date. Numbers come from
`measure.py`; name the snapshot files.

## CH-001: [short name of the change]

- Status: planned | live | measuring | kept | reverted | extended
- Hypothesis: Changing [what] on [page set] raises [metric] by at least [size] within [window], because [reason
  from a measured finding].
- Change type: [title and description | content | internal links | indexing fix | page speed | other: ...]
- Treated set: `docs/growth/sets/CH-001-treated.txt` ([n] pages)
- Control set: `docs/growth/sets/CH-001-control.txt` ([n] pages; same template, similar impressions, same market)
- Primary metric: [clicks | CTR | impressions | sign-up clicks], direction [up | down], minimum size [x %]
- Secondary metrics: [position per query, conversions per landing page]
- Baseline snapshot: `docs/growth/snapshots/YYYY-MM-DD-baseline.json`, window YYYY-MM-DD to YYYY-MM-DD
- Shipped: YYYY-MM-DD, commit or deploy reference
- Live HTML confirmed: YYYY-MM-DD
- Recrawl confirmed (URL Inspection `lastCrawlTime`): YYYY-MM-DD for [n] of [n] pages
- Re-measure date: recrawl + 28 days + 3 days lag = YYYY-MM-DD
- Revert condition: difference in differences on the primary metric below [x] points, or negative
- External events during the window: [core update, outage, campaign, tracking change, none]
- Outcome: [claimable yes/no; treated [x %], control [y %], difference [z] points; per-query position notes]
- Decision: [kept | reverted on YYYY-MM-DD | extended to YYYY-MM-DD], reason in one line
