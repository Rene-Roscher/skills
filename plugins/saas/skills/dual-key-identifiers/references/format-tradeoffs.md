# Public ID format trade-offs

Load when choosing or changing the public ID format, or when someone proposes a time-ordered format for index
performance. The default is a NanoID over `0-9a-zA-Z`. Anything else needs the ADR at the end of this file.

## What each format reveals and costs

| Format | Random bits | Reveals | Insert pattern in the `public_id` unique index | Length |
|---|---|---|---|---|
| NanoID, 21 chars, `0-9a-zA-Z` (default) | about 125 (21 × log2 62) | nothing | scattered | 21 |
| NanoID, 21 chars, `A-Za-z0-9_-` | 126 | nothing | scattered | 21 |
| UUIDv4 | 122 | nothing | scattered | 36 (with hyphens) |
| UUIDv7 | at most 74 | creation time to the millisecond, creation order | sequential | 36 |
| ULID | 80 | creation time to the millisecond; in monotonic mode, IDs from the same millisecond follow from one another | sequential | 26 |
| Timestamp-first COMB UUID (for example a framework's "ordered UUID") | fewer than 122 | creation time | sequential | 36 |

Sources: RFC 9562 §5.4 and §5.7 (https://www.rfc-editor.org/rfc/rfc9562.html), ULID spec
(https://github.com/ulid/spec), NanoID README (https://github.com/ai/nanoid), all verified 2026-10-31. The 125-bit
figure is computed, not quoted. The UUIDv7 random-bit ceiling is 128 minus the 48-bit timestamp, 4 version bits and
2 variant bits; implementations that use part of it as a counter have fewer.

## How to read the trade-off

- Random formats spread inserts across the unique index. On large, write-heavy tables that means more page splits
  and a larger working set. With the two-key design, joins and foreign keys still use the ordered bigint, so the
  cost is limited to the one unique index on `public_id`. Measure it on the target engine before calling it a
  problem.
- Time-ordered formats keep that index append-mostly, and they publish when each record was created. For accounts,
  customers, invoices and tenants, creation time and volume are business data: a competitor who signs up twice a
  month can read growth from the IDs.
- A time-ordered format is defensible where creation time is already public, such as log lines or public events.
  The ADR says why it is public there.

## Generation, per platform

Use the platform CSPRNG and an unbiased mapping onto the alphabet. Pick one place in the code that mints IDs.

- PHP: `random_int(0, 61)` per character is uniform and cryptographically secure
  (https://www.php.net/manual/en/function.random-int.php, verified 2026-10-31). If you use a NanoID port, read which
  mode reaches `random_bytes`; in hidehalo/nanoid-php the default `generateId()` mode uses `mt_rand()`, while
  `formattedId()` with a custom alphabet goes through its `random_bytes` generator
  (https://github.com/hidehalo/nanoid-php, source verified 2026-10-31).
- JavaScript and TypeScript: the `nanoid` package's `customAlphabet(alphabet, size)` returns a generator for a custom
  alphabet. Do not use the `nanoid/non-secure` entry point, which the README describes as for environments without
  hardware random generators (https://github.com/ai/nanoid, verified 2026-10-31).
- Go: `crypto/rand`, never `math/rand`.
- Python: `secrets.choice` over the alphabet.

## Validation pattern

- Accept exactly the generated length and alphabet, for example `^[0-9A-Za-z]{21}$`.
- If an older alphabet included `-` and `_`, keep the pattern at `^[0-9A-Za-z_-]{21}$` for lookups so stored links
  resolve. Generation uses the new alphabet; lookup accepts both.
- The pattern only rejects garbage early. Existence and tenant come from the scoped query.

## Shape test

- Generate 1,000 IDs; assert each matches the pattern and all are distinct.
- For a random format, assert that two IDs generated back to back share no common leading run longer than chance
  would give. This catches a time-ordered generator configured by mistake. It is a sanity check, not a randomness
  proof.

## ADR template

```markdown
# ADR: public ID format for [entity or project]

Status: proposed | accepted
Date: YYYY-MM-DD

## Decision
Public IDs for [entities] use [format], [length] characters over [alphabet], minted by [generator] using [CSPRNG].

## What the format reveals
[Nothing beyond existence | creation time to the millisecond | creation order]. This is acceptable because [reason].

## Index cost
[Scattered or sequential] inserts into the `public_id` unique index. Measured on [engine and version]: [result].

## Why not the default
[Reason the NanoID default does not fit.]

## Consequences
Validation pattern: [regex]. Old alphabets still accepted for lookup: [yes/no].
```
