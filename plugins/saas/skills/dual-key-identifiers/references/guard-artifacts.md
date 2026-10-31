# Guard artifacts for identifiers

Load when building or extending the leak guard, adding an allowlist entry, writing egress-channel tests, or adding
schema checks. Each artifact turns one rule from SKILL.md into a check that fails the build.

## Contents

- Response-scanning leak guard
- Guard self-test
- Egress-channel payload tests
- Duplicate-index check
- Static grep gates
- API schema lint
- Paired 404 helper
- Mass-assignment test

## Response-scanning leak guard

Install it once in the base test case, so every feature test runs through it.

- Hook: a test-only middleware or response listener that sees the final response of each request the suite makes.
- What it inspects: JSON bodies; server-rendered page props (for an Inertia-style app, the `data-page` JSON); the
  `Location` header; every string that looks like a pagination URL or cursor, decoded from base64url JSON.
- What fails: a key named `id`, ending in `_id` or `Id`, or ending in `_ids` or `Ids`, whose value is an integer, a
  digit-only string, or a list containing either. A `Location` or URL value with a digit-only path segment.
- Modes: `fail` (default in CI), `report` (writes one JSONL line per finding, for triaging legacy code), `off`
  (local debugging only; CI rejects it).
- Allowlist: a short file of `key-or-path reason` lines. Typical entries are a third-party platform's numeric key
  (for example a chat platform's numeric chat ID) and staff-only or machine-to-machine paths. An entry without a
  reason is a load error. Review every new entry like code.
- Failure message: the test name, the request path, the JSON path of the value and the key. Never print the whole
  body, which may hold personal data.

`scripts/scan_id_leaks.py` implements the same key check for captured payloads outside the HTTP pipeline and for the
guard's `report` output. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/scan_id_leaks.py --help`.

## Guard self-test

A guard that matches nothing passes silently. Feed it every shape and assert the verdict.

| Shape | Example | Expected |
|---|---|---|
| integer `id` | `{"id": 42}` | leak |
| digit string | `{"customer_id": "42"}` | leak |
| id list | `{"line_item_ids": [1, 2]}` | leak |
| camelCase | `{"invoiceId": 7}` | leak |
| nested | `{"data": {"customer": {"id": 9}}}` | leak |
| cursor | `{"next_cursor": "[base64url of {\"id\":42}]"}` | leak |
| cursor inside URL | `{"next_page_url": "/invoices?cursor=[same]"}` | leak |
| numeric path | `Location: /invoices/42` | leak |
| public ID | `{"id": "V1StGXR8Z5jdHi6BmyT0a"}` | clean |
| allow-listed key | `{"chat_id": 123}` with an allowlist entry | clean |
| count field | `{"invoice_count": 3}` | clean |

Then mutate production code once (emit the internal key from one serializer) and confirm the suite turns red.

## Egress-channel payload tests

These channels do not pass the HTTP pipeline, so the guard never sees them. Give each one a test that captures the
real payload and runs the key check.

- Broadcasts: capture the event's channel names and payload. Channel names use the public ID, for example
  `tenant.{publicId}`.
- Mails: render the mailable to HTML and text and scan both, including links. A faked mailer that only records the
  class name proves nothing about content.
- Outbound webhooks: capture the signed body before it is sent.
- Exports: generate the file in the test and scan each row (CSV) or document (JSON).
- Queued notifications: build the notification for a real recipient and scan each channel's representation.

Write captured payloads to a temporary directory as JSON or JSONL and run the script over it, or call the same
check in-process.

## Duplicate-index check

Run against the migrated test database in CI. It reports index groups on the same table with the same columns,
operator classes, expressions and predicate, which is how a `unique()` plus `index()` on `public_id` shows up.

```sql
SELECT key, array_agg(idx) AS duplicate_indexes
FROM (
  SELECT indexrelid::regclass AS idx,
         indrelid::text || ' ' || indclass::text || ' ' || indkey::text || ' ' ||
         coalesce(indexprs::text, '') || ' ' || coalesce(indpred::text, '') AS key
  FROM pg_index
) sub
GROUP BY key
HAVING count(*) > 1;
```

The CI step fails when the query returns a row. Source: PostgreSQL wiki, Index Maintenance, "Duplicate indexes"
(https://wiki.postgresql.org/wiki/Index_Maintenance, verified 2026-10-31).

## Static grep gates

Strip comments first, then fail CI on:

- `public_id ??` or `publicId ??` in serializer or resource classes.
- `->id` or `.id` emitted under an `id` key in serializer classes, outside an allowlist.
- Direct calls to the ID library outside the one generator class.
- `orderBy('id')` or an equivalent sort on the internal key in front of cursor pagination.

## API schema lint

In the OpenAPI document, every property named `id` or ending in `_id` or `_ids` (items) has `type: string`. Run it in
the same CI job that publishes the schema.

## Paired 404 helper

A helper such as `assertSameAsMissing(foreignUrl)` requests the foreign URL, a URL with a random well-formed ID and a
URL with a malformed ID, then asserts equal status and equal body after removing request IDs and timestamps. Every
resource's tests call it for show, update and delete.

## Mass-assignment test

Create a record through the public endpoint with `public_id` and `id` in the body. Assert the stored public ID differs
from the supplied one and the internal key was not taken from input.
