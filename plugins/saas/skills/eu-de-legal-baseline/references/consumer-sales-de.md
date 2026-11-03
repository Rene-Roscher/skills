# Selling to consumers in Germany

Review-ready draft, not legal advice. Scope: Germany. Statute text read on gesetze-im-internet.de on 2026-11-03.

## Who is a consumer

- BGB § 13: a natural person who concludes a transaction for purposes that are "überwiegend weder ihrer
  gewerblichen noch ihrer selbständigen beruflichen Tätigkeit" attributable.
- BGB § 14: an Unternehmer is a natural or legal person or partnership acting in its commercial or independent
  professional capacity.
- The test is the purpose of the contract. A freelancer buying a tool for client work is a business; the same
  person buying it for a hobby club is a consumer.

## B2B-only offers

- Write the decision into an ADR: who may sign up, how the product checks it, and what happens when a consumer
  slips through.
- Typical controls, from light to strict: a mandatory business confirmation with stored wording version and
  timestamp; company name and address; a VAT ID validated against VIES (see `billing-eu-b2b`); manual review
  for edge cases. How much proof is enough is the lawyer's call.
- Enforce it on the server. A form-only check lets API clients and old app versions through.
- Keep the copy consistent: pricing pages that show net prices "plus VAT" and a "for businesses" note match the
  B2B-only decision; a "free for personal use" tier contradicts it.
- B2B-only also keeps BFSG out of scope (its services list covers services to consumers).

## The consumer pack

Everything below applies once consumers can conclude contracts online.

| Duty | Statute | What to build |
|---|---|---|
| Information before the order, incl. withdrawal information | BGB § 312d with Art. 246a EGBGB (not re-read, Unverified) | pre-order page; withdrawal notice text from the lawyer |
| Withdrawal period of 14 days for distance contracts | BGB § 312g Abs. 1, § 355 Abs. 2 | record contract date; handle withdrawals inside the window |
| Withdrawal right lapses at the latest 12 months and 14 days after the start if information was missing | BGB § 356 Abs. 3, 4 | send the withdrawal information on a durable medium |
| Service started during the period: consumer owes value only after an express request to start and proper information | BGB § 356 Abs. 5, § 357a Abs. 2 | checkbox "start now" with stored wording; pro rata of the agreed total price |
| Order button labelled "zahlungspflichtig bestellen" or an equally clear wording; otherwise no contract | BGB § 312j Abs. 3, 4 | exact button text; tests on every checkout path |
| Kündigungsbutton "Verträge hier kündigen", confirmation page with "jetzt kündigen", stored declaration, immediate confirmation in text form | BGB § 312k | always reachable cancel page; confirmation email with date and time |
| Without the button the consumer may terminate at any time without notice | BGB § 312k Abs. 6 | treat a broken cancel flow as a P1 bug |
| Withdrawal function "Vertrag widerrufen" and "Widerruf bestätigen", available for the whole withdrawal period, receipt on a durable medium | BGB § 356a, from 19 June 2026 | second button set next to the cancel flow |
| Total price including VAT | PAngV § 3 Abs. 1 | consumer mode shows gross prices |
| Initial term at most 2 years; tacit renewal only to an indefinite term cancellable monthly; notice at most 1 month | BGB § 309 Nr. 9 | plan config validation for consumer plans |

## Open questions for the lawyer

- Whether the SaaS is a service or a digital product (BGB §§ 327 ff.) for withdrawal and value compensation.
  The answer changes how the right lapses and what can be charged after a withdrawal.
- Whether the cancel and withdrawal functions may sit behind a login when the contract itself requires an
  account. The statutory text requires the functions to be permanently available and easy to reach;
  commentary on the login question was not checked against a primary source (Unverified).
- Consumer VAT (destination principle, OSS) is outside `billing-eu-b2b`; ask the tax adviser before the first
  consumer sale.

## Engineering checks

- An end-to-end test on a consumer account: order button label; cancel page reachable from the footer of every
  page; withdrawal page reachable during the window; both confirmation emails arrive with date and time.
- A configuration test: no consumer plan with a term over 24 months, renewal other than indefinite with one
  month's notice, or notice over one month.
- A snapshot test of the pricing page in consumer mode: gross prices, VAT included.
