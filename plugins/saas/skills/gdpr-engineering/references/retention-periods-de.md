# Retention periods in Germany

Review-ready draft, not legal or tax advice. Scope: Germany. Confirm the classes that apply to your records with
your tax advisor. Sources: https://www.gesetze-im-internet.de/ustg_1980/__14b.html and
https://www.gesetze-im-internet.de/ao_1977/__147.html (verified 2026-10).

## Periods

| Record | Period | Basis |
|---|---|---|
| Invoices you issue and receive | 8 years | UStG § 14b Abs. 1 |
| Books and records, inventories, annual financial statements, management reports, opening balance sheet, related work instructions | 10 years | AO § 147 Abs. 1 Nr. 1, Abs. 3 |
| Accounting vouchers (Buchungsbelege) | 8 years | AO § 147 Abs. 1 Nr. 4, Abs. 3 |
| Received and copies of sent business letters (Handels- oder Geschäftsbriefe), other documents relevant for taxation | 6 years | AO § 147 Abs. 1 Nr. 2, 3, 5, Abs. 3 |

## When the period starts

- Invoices: at the end of the calendar year in which the invoice was issued (UStG § 14b Abs. 1 Satz 3).
- AO records: at the end of the calendar year in which the last entry was made, the document was created, or
  the letter was received or sent (AO § 147 Abs. 4).

So an invoice issued in March 2026 may be deleted from 1 January 2035, not in March 2034.

## How this meets erasure

- GDPR Art. 17(3)(b) lifts the erasure duty to the extent processing is needed for a legal obligation. Keep the
  record, restrict access to the people who need it, and clear fields the record does not need (for example a
  login history attached to the customer record).
- Store the retention end date on the record (`retain_until`), computed from the rule above, so the cleanup job
  does not recompute law.
- Invoice content is defined by `billing-eu-b2b`; this table only says how long it stays.
