# Claims table: [path of the page file]

One row per product claim on the page: feature, limit, price, integration, location, certification, number.
Copy this file next to the page change (for example `docs/claims/[page].md`) and run
`check_claims.py --table [this file] --root . --page [page file]` before the page ships.

- value as on page: the value exactly as the page shows it, without the surrounding sentence (`150`, not
  "Up to 150 services"). The script finds it on the page and within two lines of the cited source line.
- source: `path/to/file:line` or `path/to/file:12-14` relative to the repository root, pointing at the code,
  config or spec that sets the value. Without such a line, a dated record: `record YYYY-MM-DD: [what and
  where]`, or an external URL with its read date. Another marketing page, a translation file or the page itself
  is never a source.
- checked on: the date you compared value and source, `YYYY-MM-DD`.
- A claim with no source is removed from the page, not kept with an empty row.

| claim | value as on page | source | checked on |
|---|---|---|---|
| [what the page claims] | [value as shown] | [path/to/file:line or record YYYY-MM-DD: ...] | [YYYY-MM-DD] |
