# Subprocessors and transfers

Review-ready draft, not legal advice. Scope: EU (GDPR Art. 28, 44-46). Sources:
https://eur-lex.europa.eu/eli/reg/2016/679/oj and
https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en
(verified 2026-10).

## Subprocessor or not

| Situation | Classification |
|---|---|
| You hold the account and API key (mail, SMS, push, storage, error tracking, hosting) | subprocessor |
| The customer enters their own endpoint (their chat webhook, their SIEM) and you deliver to it | customer-directed, not your subprocessor |
| The customer connects their own account at a provider with their credentials | customer-directed; document it |
| A provider's own subprocessor (its cloud host) | chain link: list it under the provider entry, not as a separate entry |
| A sub-entity of the provider that signs nothing with you | chain link |

List the entity that signs the contract and the country where processing happens. A brand name is not enough.

## Adding a subprocessor

1. Add the `subprocessors.yaml` entry (entity, country, data, code, hosts, transfer basis).
2. Check the provider's own chain for processing outside the EU/EEA.
3. Follow the change procedure in your AVV. Art. 28(2) requires informing the controller of the intended addition
   or replacement and giving the opportunity to object. The notice period is whatever your AVV says.
4. Send the notice as an external action under `safe-actions`; keep a record of when and to whom.
5. Go live only after the notice period, or with the controllers' agreement.

## Transfer basis

| Where processing or access happens | Basis |
|---|---|
| EU/EEA | none needed for Chapter V |
| A country or framework on the Commission's adequacy list | Art. 45 adequacy decision; check the list on the day you decide |
| Elsewhere | Art. 46 safeguards, usually standard contractual clauses, plus a transfer impact assessment (counsel work) |

Support or on-call staff who access data from outside the EU/EEA can make the access itself a transfer. Treat it
as one in the inventory and ask counsel to confirm the basis.

## Code defaults match the contract

- Every location, region or provider option carries a `third_country` flag.
- Defaults return only EU/EEA or adequacy options when the contract describes others as opt-in.
- A test asserts the default selection and fails when someone adds a third-country location as default.
- Moving a bucket, queue or database to another region is a trigger: subprocessor entry, transfer basis, and any
  hosting claim in `claims.yaml`.
