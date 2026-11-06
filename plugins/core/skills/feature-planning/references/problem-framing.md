# Problem framing

Load this when the request names a solution ("add a button", "we need a toggle"), or when the personas and the
stress moment are unclear. The goal is the eight Problem fields, written without any technology in them.

## From solution to problem

Ask, or find out from tickets and code:

- What does the person do right before they would click the new button? What do they do right after?
- What do they do today instead, and what does that cost them (time, errors, a support ticket, a spreadsheet)?
- What happens if we don't build it?

Example: "Add an export button to the invoice list" becomes "The external auditor needs every invoice of last
quarter with its payment status; today an accountant copies them by hand, which takes a day and misses credit
notes."

## Personas

Name each kind of person who touches the feature. They expect different things:

- the person who uses it daily (an accountant, a project lead, a front-desk clerk);
- the person who pays for the product and judges it (an owner, a finance lead);
- the person who configures or automates it (an admin, a developer using the API);
- the person outside the customer who sees the result (an invoice recipient, a guest with a booking).

## Business goal

The persona's need says why someone uses the feature; the business goal says why the project builds it now. Read
it from the product brief, the business model or the issue, and name the source: more revenue (an upsell, a plan
axis), retention (a cancellation reason removed), lower cost (support tickets, manual work), or an obligation (a
law, a contract). If none of these can be named, say so in the plan: the feature may not be worth its cost, and the
owner decides.

## Success moment and metric

- Success moment: the moment the persona notices it works, in their words. "The auditor gets one file and has no
  follow-up questions."
- Success metric: a number you can measure after release, and where it comes from. "Exports per month; support
  tickets tagged export drop to zero within two months."

## Non-goals

List what the plan does not do, especially what a reader would assume it does. "No scheduled exports. No custom
column selection. No PDF."

## Stress moment

The moment of highest stress in which the feature is used. Plan for it, not for the demo.

| Product | Stress moment |
|---|---|
| Invoicing app | Month-end close, with the auditor waiting |
| Booking system | The minute a sold-out event opens for booking |
| Project tool | The day before a client deadline, with five people editing |
| Support desk | An outage, with hundreds of tickets in an hour |

Ask what breaks for the persona in that moment: speed, clarity, permissions, volume, an action that can't be
undone.
