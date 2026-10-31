# VAT treatment, EU and Germany

Load for tax treatment, VAT IDs, reverse charge and the VIES response. Review-ready draft for the DE/EU scope,
not legal or tax advice. Scope: a seller established in Germany selling electronically supplied or other
services to business customers. Sources checked 2026-10-31.

## Legal basis in one paragraph each

- Place of supply for services to a taxable person is where the customer is established (VAT Directive
  2006/112/EC Art. 44; in Germany UStG § 3a Abs. 2).
- For such services from a supplier not established in the customer's Member State, the customer owes the VAT
  (Art. 196). The seller invoices without VAT and states the reverse charge (Art. 226 point 11a; in Germany
  UStG § 14a Abs. 1, see the German invoice reference).
- Wrongly applied reverse charge leaves the seller owing the VAT it did not charge.

## Treatment matrix

| Buyer established in | Business confirmed | VAT ID confirmed | Treatment |
|---|---|---|---|
| Germany | yes | not needed for the treatment | domestic VAT at the German rate |
| Other EU Member State | yes | yes, with stored proof | reverse charge: net only, category AE, rate 0 |
| Other EU Member State | yes | no, invalid, unavailable or name mismatch | not reverse charge; follow the project's documented policy |
| Outside the EU | yes | | outside this table; decide with the tax advisor |
| Anyone | no | | outside this skill (consumer sales) |

The resolver takes every column as an explicit argument and returns the treatment, the rate and the VAT
category. It has no default rate. Renewal jobs call it with values loaded from the subscription's customer,
never from request or tenant context.

## VIES

The REST API's OpenAPI description (https://ec.europa.eu/assets/taxud/vow-information/swagger_publicVAT.yaml,
verified 2026-10-31) returns for a VAT number check:

- `countryCode`, `vatNumber`, `requestDate`, `valid` (boolean), `requestIdentifier`, `name`, `address`;
- `traderName`, `traderStreet`, `traderPostalCode`, `traderCity`, `traderCompanyType`;
- match fields such as `traderNameMatch`, each one of `VALID`, `INVALID`, `NOT_PROCESSED`.

"In order to retrieve the requestIdentifier, the information about requesterMemberStateCode and
requesterNumber have to be provided." Configure the seller's own VAT ID as requester so each check yields an
identifier. Errors come back in a common response with error wrappers (code and message); treat every error
and every timeout as "not confirmed".

## Confirmation rule

- Format check first (country prefix and pattern), then the registry call.
- Confirmed means `valid` is true and the name check passes: a `VALID` name match, or a returned `name` that
  matches the customer's legal name after normalisation. When the registry publishes no name, record that and
  apply the project's policy.
- Store: number as checked, `valid`, returned name, match result, `requestIdentifier`, `requestDate`, and the
  raw response.
- Check again when the customer changes the number, and on a schedule for active reverse-charge customers. An
  invoice keeps the treatment that was true when it was issued.

## Decisions for the tax advisor

These are not engineering defaults. Record the answers in the project profile:

- What to charge while a number is unconfirmed (domestic VAT now and a correcting credit note later, or no
  sale until confirmed).
- Whether a national confirmation (in Germany through the federal tax office) is wanted in addition to VIES.
- Treatment of customers outside the EU.
