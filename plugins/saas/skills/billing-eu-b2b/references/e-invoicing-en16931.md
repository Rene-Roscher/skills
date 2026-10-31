# E-invoicing with EN 16931

Load for e-invoice output, credit notes, allowances, XRechnung or ZUGFeRD, and validator setup. Rule texts are
quoted from the EN 16931 schematron in https://github.com/ConnectingEurope/eInvoicing-EN16931 (CII model,
read 2026-10-31).

## Rules that shape the data model

| Rule | Text |
|---|---|
| BR-27 | "The Item net price (BT-146) shall NOT be negative." |
| BR-28 | "The Item gross price (BT-148) shall NOT be negative." |
| BR-CO-10 | "Sum of Invoice line net amount (BT-106) = Σ Invoice line net amount (BT-131)." |
| BR-CO-11 | "Sum of allowances on document level (BT-107) = Σ Document level allowance amount (BT-92)." |
| BR-CO-14 | "Invoice total VAT amount (BT-110) = Σ VAT category tax amount (BT-117)." |
| BR-CO-15 | "Invoice total amount with VAT (BT-112) = Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110)." |
| BR-CO-17 | VAT category tax amount (BT-117) = taxable amount (BT-116) × rate (BT-119) / 100, rounded to two decimals |
| BR-AE-02 | A reverse-charge line requires the seller's VAT identifier (or tax registration or tax representative identifier) and the buyer's VAT identifier (or legal registration identifier) |
| BR-AE-05 | On a reverse-charge line, the item VAT rate (BT-152) is 0 |
| BR-AE-08 | The reverse-charge taxable amount equals the reverse-charge line net amounts minus allowances plus charges in that category |
| BR-AE-09 | The reverse-charge category tax amount (BT-117) is 0 |
| BR-AE-10 | A reverse-charge VAT breakdown has an exemption reason code (BT-121) or the text "Reverse charge" (BT-120) |

No rule in the core model forbids a negative invoiced quantity (BT-129); BR-27 and BR-28 restrict prices only.

## Credits and discounts

- A discount on the whole invoice is a document-level allowance (BG-20) with an amount (BT-92) and a VAT
  category (BT-95). The allowances add up to BT-107.
- A credit for a previous period, or a refund of a line, is a negative quantity at a positive price, or a
  separate credit note document. Check that your CIUS (XRechnung, a ZUGFeRD profile) and the receiving
  accounting system accept negative quantities before you rely on them.
- Never a line with quantity 1 at a negative price. It renders as a PDF and fails BR-27.
- Charge equals invoice: the PSP charge is BT-112 of the invoice, computed by the same function.

## Validator in CI

- Use the KoSIT validator (https://github.com/itplr-kosit/validator, Apache-2.0). It has no rules of its own;
  it runs validation scenarios, and the XRechnung configuration is a separate release
  (https://github.com/itplr-kosit/validator-configuration-xrechnung).
- Invocation form from the README: `java -jar validator-[version]-standalone.jar -s [scenarios.xml]
  [-r repository-path] [files]`. Run `--help` at the pinned version for the reporting options.
- Pin both releases and verify their checksums in the CI job. Never fetch "latest".
- Golden invoices to validate: domestic, reverse charge, credit line, coupon, add-on, proration, and a credit
  note. The build fails on any error, and on any warning that is not allowlisted with a reason.
- Re-run the golden set when the validator or configuration release changes; rule sets are versioned.
