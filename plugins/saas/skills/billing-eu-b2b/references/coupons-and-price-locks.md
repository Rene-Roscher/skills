# Coupons and price locks

Load for discounts, price locks and campaign promises. The example is a booking system with monthly and annual
plans and a launch campaign.

## Discount rules

- A discount reduces the net amount; VAT is computed on the reduced net.
- A discount stays strictly below the net price of what it applies to. Computed discounts (percent of a
  prorated amount, stacked coupons) are capped at net minus one minor unit, or the coupon is refused.
- A zero total is a separate state, not a side effect. Code paths that treat zero as "free plan" must never see
  a paid subscription with a 100 % discount.
- On an e-invoice, a discount is an allowance on the line or the document, never a negative price.
- A database CHECK constraint ties the coupon kind to its value column: a percentage between 1 and 99, or a
  positive fixed amount in minor units.

## Adding a discount kind

A guard such as `if (percent <= 0) return;` was correct while every coupon was a percentage. A fixed-amount
coupon has no percentage and is skipped silently. When adding a kind:

1. Search the billing code for every condition on the existing kinds' fields.
2. Walk each money path: checkout, renewal, proration, preview, customer notices, invoice rendering, refunds.
3. Write one test per kind per path.
4. Decide how a fixed amount behaves under proration and period switches, and write that into the coupon's
   documentation.

## Price locks

- A price lock is stored on the subscription when it is bought: the locked price, currency, interval and the
  promise it came from (campaign, contract).
- A catalogue change never touches locked subscriptions. A global flag that turns locks on or off can end every
  lock at once, including for the customers the promise was made to.
- Worst case: compute the locked price combined with every permanent coupon the subscription can carry. The
  result must stay above zero and above the floor the business accepts.

## Server-side catalogue

- Price, plan, quantity and currency come from the server catalogue. A request that sends them is ignored for
  those fields.
- Staff plan changes start from the current plan and show the immediate charge and the downgrade effects
  before confirming. If moving a complimentary account to paid billing charges at once, the confirmation says so.
