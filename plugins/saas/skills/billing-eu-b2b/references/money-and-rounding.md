# Money and rounding

Load when computing any amount, VAT, proration or discount, or when choosing a money library.

## Representation

- Store amounts as integers in minor units (cents) in a 64-bit column, with the ISO 4217 currency code next to
  them. Or use an exact decimal type end to end. Never a binary float, in the database or in code.
- Rates are integers too: basis points (1900 = 19 %) or an exact decimal string. A rate is a parameter of the
  computation, never a literal default.
- The library choice is free. brick/money is one PHP example: its README states that operations needing
  rounding throw `RoundingNecessaryException` unless a `RoundingMode` is passed (verified 2026-10-31). Check
  the rounding API at the version in your lockfile before relying on it.
- In JavaScript, `Number` is a binary float. Keep cents as integers (or `BigInt`) and use `Intl.NumberFormat`
  for display only.

## Integer recipes

Tax for a non-negative net amount with the rate in basis points, rounding half up:

```text
tax   = intdiv(net * rate_bp + 5000, 10000)
gross = net + tax
```

For a negative amount (credit note), mirror the sign so rounding stays half away from zero:

```text
tax = -intdiv(-net * rate_bp + 5000, 10000)
```

Checked 2026-10-31 against exact decimal half-up rounding for nets from -200000 to 200000 at 1900, 700, 2100,
2000 and 1950 basis points: no mismatch.

Per invoice, compute tax per VAT category on the sum of the line net amounts in that category, then round
once (EN 16931 BR-CO-17). Rounding per line and summing can differ by a cent.

Proration with a documented time basis, rounding half up:

```text
part = intdiv(price * remaining_seconds + period_seconds / 2, period_seconds)
```

When splitting one amount into parts (a document discount across lines, a credit across periods), compute all
parts but the last, and set the last part to the whole minus their sum. The parts then always add up to the
whole.

## Why floats fail, reproduced

```php
(int) round(250 / 100 * 1.19 * 100)
```

The float is 297.49999999999994. PHP 8.3.10 returns 298, PHP 8.4.27 returns 297 (both run 2026-10-31). PHP
8.4 removed the internal "pre-rounding" of `round()` (php-src `UPGRADING`, PHP-8.4 branch: "Fixed a bug
caused by 'pre-rounding' of the round() function"). The exact value is 297.5, so half up gives 298. The
integer recipe gives tax 48 and gross 298 on every version.

## Runtime parity

- Pin the production PHP version once (for Composer, `config.platform.php`) and make the test bootstrap abort
  when the running minor version differs.
- Run money tests in the production image, not only on a developer host.

## Guard

A static rule or a small script fails the build on these in the billing code, outside one allowlisted money
helper: float casts, `round`, `floor`, `ceil`, `/` on amount variables, and float literals multiplied with
amounts. Each allowlist entry carries one line of reason.
