# Role and artifacts

Review-ready draft, not legal advice. Scope: EU (GDPR). Source: GDPR Art. 4(7)-(8), 6, 13, 26, 28, 30,
https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10).

## Deciding the role

Ask one question per data set: who decides why the data is processed and by which means?

- Your customer decides, you process on their instructions: you are **processor** (Auftragsverarbeiter, Art. 4(8)).
- You decide for your own purposes: you are **controller** (Verantwortlicher, Art. 4(7)).
- You and another party decide together: **joint controllers** (Art. 26). Take this to counsel; it needs an
  arrangement between the parties.

A B2B SaaS is almost always both, for different data sets. Example, an invoicing app:

| Data set | Role | Why |
|---|---|---|
| Invoices, line items and the customer's own clients | processor | the customer decides what to invoice and to whom |
| Account owner and team members of the customer (signup, login) | controller | you need it to run your contract |
| Your billing of the customer | controller | your own legal and tax duties |
| Support requests | controller | you decide how support works |
| Product analytics you run | controller | your own purpose |
| Comments users post on your public roadmap | controller | your surface, your moderation |
| Free text a customer's system sends into your product (logs, agent output) | processor | it is the customer's data, even when unexpected |

## Artifacts per role

| Role | Artifact | Basis |
|---|---|---|
| processor | AVV (DPA) with the content of Art. 28(3) | Art. 28(3) |
| processor | TOM annex | Art. 28(3)(c), 32 |
| processor | subprocessor annex and the change procedure | Art. 28(2), 28(4) |
| processor | VVT for processors | Art. 30(2) |
| controller | privacy notice | Art. 13 (data from the person), 14 (from elsewhere) |
| controller | VVT for controllers | Art. 30(1) |
| controller | legal basis per purpose | Art. 6(1) |
| controller | DSFA triage, DSFA where needed | Art. 35 |
| controller | data-subject request handling | Art. 12, 15-22 |

## Consequences that are easy to miss

- A change to controller data (a new analytics tool, a public comment feature) updates the privacy notice and
  the VVT. It does not re-trigger the AVV's subprocessor procedure, because the AVV covers processor data only.
- A new provider that touches processor data does trigger the subprocessor procedure, even when it is small,
  such as a push or SMS provider whose account you hold.
- The same provider can appear in both roles: an error tracker receives processor data (customer payloads in
  stack traces) and controller data (your users' IP addresses). List it in both places.
- Data subjects of processor data are the customer's people. Their requests go to the customer; your AVV says how
  you assist.
