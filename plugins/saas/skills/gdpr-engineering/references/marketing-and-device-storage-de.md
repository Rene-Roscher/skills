# Promotional email and device storage in Germany

Review-ready draft, not legal advice. Scope: Germany. Sources: https://www.gesetze-im-internet.de/uwg_2004/__7.html,
https://www.gesetze-im-internet.de/ttdsg/__25.html (verified 2026-10).

## Promotional email (UWG § 7)

- § 7 Abs. 2 Nr. 2: advertising by electronic mail without the addressee's prior express consent is always an
  unreasonable nuisance. The provision speaks of the addressee, so business recipients are covered as well.
- § 7 Abs. 3, the existing-customer exception, needs all four conditions:
  1. the address was obtained from the customer in connection with the sale of goods or a service,
  2. it is used for direct advertising of your own similar goods or services,
  3. the customer has not objected, and
  4. the customer is told clearly, at collection and at every use, that they can object at any time without
     costs beyond the basic transmission rates.

## What the dispatcher enforces

- Every message type declares its purpose: transactional (receipt, password reset), service (an operational
  notice the customer configured), or promotional (newsletter, upsell, lifecycle nudge).
- Promotional sends require a consent record or an exception record that documents all four conditions.
  Without one, the send throws.
- Promotional mail carries an opt-out link and a `List-Unsubscribe` header. Transactional mail does not pretend
  to be one or the other.
- Contact data collected for operational notifications (alert recipients, emergency contacts) is never selected for
  promotion.
- No open-tracking pixels by default. If clicks are measured, use a signed redirect and record it in the VVT.

## Uncertain cases

Review requests, satisfaction surveys and "how is it going" lifecycle mails may count as advertising. Ask
counsel, record the decision, and do not cite court decisions from memory.

## Device storage (TDDDG § 25)

- Abs. 1: storing information on the user's device or reading it from there is only allowed with consent based
  on clear and full information.
- Abs. 2 Nr. 2: no consent is needed where the storage or access is strictly necessary so that the provider of a
  digital service can provide a service the user explicitly asked for.

Method: list every cookie, local storage and session storage key the app sets before any consent. Give each one
a reason and decide whether it is strictly necessary for the service the user asked for. Typical: a login session
cookie or a CSRF token is necessary for a logged-in app; analytics and marketing tags are not. When a key is
unclear, ask counsel and write down the answer. A browser test compares the observed keys with the allowlist.
