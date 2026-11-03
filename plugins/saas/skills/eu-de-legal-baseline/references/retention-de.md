# Retention of business records after the 2025 change

Review-ready draft, not legal or tax advice. Scope: Germany. Statute text read on gesetze-im-internet.de on
2026-11-03. Confirm the classes that apply to your records with the tax adviser. Deletion mechanics, backups and
the GDPR side are in `gdpr-engineering`.

## Periods in force

| Record | Period | Basis |
|---|---|---|
| Invoices issued and received | 8 years | UStG § 14b Abs. 1 Satz 1 |
| Booking vouchers (Buchungsbelege) | 8 years | AO § 147 Abs. 1 Nr. 4, Abs. 3; HGB § 257 Abs. 1 Nr. 4, Abs. 4 |
| Books, records, inventories, annual accounts, management reports | 10 years | AO § 147 Abs. 1 Nr. 1, Abs. 3; HGB § 257 Abs. 4 |
| Business letters received and sent, other tax-relevant documents | 6 years | AO § 147 Abs. 1 Nr. 2, 3, 5, Abs. 3 |

- Start: the end of the calendar year of the last entry, the creation of the document, or the receipt or
  sending of the letter (AO § 147 Abs. 4, HGB § 257 Abs. 5); for invoices the end of the calendar year of issue
  (UStG § 14b Abs. 1 Satz 3).
- AO records do not expire while they matter for a tax whose assessment period is still open (AO § 147 Abs. 3).
  A tax audit or an open assessment can extend the period; the tax adviser tells you when.

## The change from ten to eight years

- The shorter periods for invoices and booking vouchers apply from 1 January 2025 to all records whose period
  under the old ten-year rule had not expired on 31 December 2024 (EGAO Art. 97 § 19a Abs. 2; UStG § 27 Abs. 40
  Satz 1).
- Exception: credit institutions, supervised insurers and investment firms keep the old rule for vouchers
  (EGAO Art. 97 § 19a Abs. 3; HGB § 257 Abs. 4 keeps ten years for their vouchers). For their invoices the
  eight years apply first to records not yet expired on 1 January 2026 (UStG § 27 Abs. 40 Satz 2).
- The change was made by the Viertes Bürokratieentlastungsgesetz of 23 October 2024, BGBl. 2024 I Nr. 323
  (HGB § 257 Abs. 4, AO § 147 Abs. 3, UStG § 14b Abs. 1 "zehn" to "acht"),
  https://www.recht.bund.de/bgbl/1/2024/323/VO.html (verified 2026-11-03). The special rule for supervised
  financial firms was changed again later; the current statute text above is what counts.

## Where it meets erasure

- GDPR Art. 17(3)(b) lifts the erasure duty as far as a legal retention duty requires the data. Keep the
  record, restrict who can read it, and clear the fields the duty does not need (login history, preferences,
  free-text notes).
- Store `retain_until` on the record, computed when it is created, so the purge job does not recompute law. An
  invoice issued in 2026 has `retain_until` of 31 December 2034 and may be deleted from 1 January 2035.
- A purge job still configured for ten years keeps records without a basis once eight years have passed; one
  configured for six deletes invoices too early. Test both edges.
