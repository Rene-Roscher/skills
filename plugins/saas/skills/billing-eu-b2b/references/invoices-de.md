# German invoice duties

Load for German invoice duties: reverse-charge wording, e-invoice dates and retention. Review-ready draft for
the DE scope, not legal or tax advice. Quotes from gesetze-im-internet.de, checked 2026-10-31.

## Reverse-charge invoices (UStG § 14a Abs. 1)

For a service under § 3a Abs. 2 performed in another Member State where the recipient owes the tax there:

- The invoice carries the wording "Steuerschuldnerschaft des Leistungsempfängers" (Satz 1). The VAT Directive
  uses "Reverse charge" for the same mention (Art. 226 point 11a).
- It is issued "bis zum fünfzehnten Tag des Monats, der auf den Monat folgt, in dem der Umsatz ausgeführt
  worden ist" (Satz 2): by the 15th of the month after the supply.
- It states the VAT identification numbers of the supplier and of the recipient (Satz 3).

## E-invoice obligation (UStG § 14 and § 27 Abs. 38)

- Between businesses established in Germany, invoices are electronic invoices in a structured format that
  conforms to EN 16931 (§ 14 Abs. 1 and 2). XRechnung and ZUGFeRD are the common syntaxes; check that the
  ZUGFeRD profile you emit is a full EN 16931 invoice, because not every profile is.
- Transitional rules in § 27 Abs. 38:

| Supplies made in | Paper or another electronic format allowed until | Condition |
|---|---|---|
| 2025 and 2026 | 31 December 2026 | other electronic formats need the recipient's consent |
| 2027 | 31 December 2027 | issuer's total turnover in the previous calendar year at most EUR 800,000 |
| 2027 | 31 December 2027 | EDI under Commission Recommendation 94/820/EC, with the recipient's consent |

- Receiving e-invoices and cross-border e-invoicing rules at EU level are outside this file. Ask the tax
  advisor and check the current EU rules before planning them.

## Retention

- Invoice copies, issued and received: eight years (§ 14b Abs. 1). "Die Aufbewahrungsfrist beginnt mit dem
  Schluss des Kalenderjahres, in dem die Rechnung ausgestellt worden ist."
- Other records by class (AO § 147 Abs. 3): ten years for books, records, inventories and financial
  statements; eight years for accounting vouchers; six years for business letters and other tax-relevant
  documents. The period starts at the end of the calendar year of the event (Abs. 4) and does not end while the
  documents matter for a tax whose assessment period is still open.
- An erasure request under GDPR Art. 17 does not delete invoices while a legal duty to keep them applies
  (Art. 17(3)(b)). How to restrict and later delete them belongs to `gdpr-engineering`.

## Engineering consequences

- Invoices are immutable. A correction is a credit note that references the original.
- The invoice stores what was true at issue: treatment, rate, both VAT IDs, addresses, prices.
- The plan for invoice output names the syntax and the date it must be live, and the CI validator runs before
  that date.
