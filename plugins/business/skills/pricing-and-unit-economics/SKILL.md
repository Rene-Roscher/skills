---
name: pricing-and-unit-economics
description: "Derives prices, plans and limits from what a customer costs: cost per unit of usage, margin at typical and at maximum use, value metric, free-tier cost per conversion, break-even, every input sourced or marked as an assumption. Use when setting or changing prices, plans, limits or a free tier, or checking that a customer pays more than it costs. Not for checkout, tax or invoices."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Pricing and unit economics

This skill decides whether a price, a plan limit or a free tier can be defended with numbers. It computes cost
per customer, margin at typical and at maximum use, the cost of the free tier per conversion and the break-even
point, from a model file in which every number names its source or is marked as an assumption. Checkout, tax
and invoice handling stay with `billing-eu-b2b`, the product and buyer with `product-strategy`. The failure it
prevents: a plan whose limits let one customer cost more than the plan earns, and a price chosen by feel that
nobody can later explain.

## Applies when / does not apply

- Applies: setting or changing prices, plans, limits, overage or a free tier; checking whether a plan makes
  money; deciding what to measure before pricing; a customer or feature that seems to cost more than it earns;
  "what should this cost", "can we afford free".
- Does not apply: who the buyer is (`product-strategy`), tax, invoices, dunning and the payment provider
  (`billing-eu-b2b`), page copy, or building the billing code (`laravel-architecture`).

## Rules

Most important first. Examples use a booking tool with SMS reminders.

- [invariant] Every input to the model carries a source (the query, the invoice or the vendor page, with its
  date) or is marked `"assumption": true`. A result that depends on an assumption is printed with a star and
  reported as an estimate. Why: a margin computed from remembered numbers looks exact and is not. Test: remove
  the source from one input; `scripts/unit_economics.py` reports `E01` and exits 1.
- [invariant] Cost per unit of usage comes from a measurement or an invoice, never from a guess about what a
  vendor charges. When you cannot measure it, mark the input as an assumption and say what would measure it.
  Why: vendor prices and your own usage change; an unmeasured cost silently becomes the basis of a price. Test:
  an input with `"assumption": true` makes every result that uses it carry a star.
- [invariant] Every cost driver of a plan has a ceiling: the plan's limit, or a measured high percentile. A
  driver without a ceiling means the cost of one customer is unbounded. Why: one tenant sending a large batch
  of SMS can erase the margin of the whole plan. Test: delete a ceiling; the script reports `E02`.
- [invariant] A plan must not lose money for a tenant at every ceiling at once. If the maximum-use margin is
  below zero, lower the limit, raise the price or meter the driver. Why: the limit is the only thing between a
  customer and your costs. Test: raise one ceiling until the cost exceeds the price; the script reports `E03`.
- [invariant] Compute margin after the payment fee, using the fee basis of the actual provider, for monthly and
  annual billing separately. Why: a fixed fee per charge weighs more on a small monthly charge than on one
  annual charge. Test: the script prints the fee per month for both cycles for a plan with an annual price.
- [invariant] Never state lifetime value from no churn. With no churned customers in the period, lifetime is
  not measurable: say so and report contribution per month. Why: dividing by a zero churn rate produces an
  infinite number that gets copied into a plan. Test: with zero churned customers the script prints `W02` and
  no lifetime figure.
- [invariant] Price changes for existing customers follow the notice and consent rules of `billing-eu-b2b`
  before any number is sent. Why: a change that is economically right can still be invalid towards the
  customer. Test: the plan for a price change names the notice period and who approved it.
- [default] Choose the value metric (the unit the price scales with) so that it grows as the customer gets
  more value and so that customers expect to pay for that unit; where cost is variable, check that it also
  tracks the cost driver that matters most. Trade-off: a metric the customer cannot predict makes the bill feel
  arbitrary. Deviate only with an ADR that names this trade-off. Source:
  https://www.willingnesstopay.com/saas-pricing-metrics, a practitioner guide, not a standard (verified
  2026-10-31).
- [default] Treat the free tier as acquisition spend: compute its monthly cost, its cost per conversion and
  the break-even with and without it, and cap every cost driver of the free plan harder than the paid ones.
  Trade-off: a strict free tier converts fewer people. Deviate only with an ADR that names this trade-off. Test:
  the script prints the free-tier cost per conversion and break-even with the free tier included.
- [default] Make limits visible to the customer and meter them in the product, so a limit is a decision the
  customer sees rather than a surprise on the invoice. Trade-off: more UI and more support copy. Deviate only
  with an ADR that names this trade-off. Source: none; this is a design judgment from operating billing
  systems, not a cited fact.

## Procedure

1. Read the product brief in `docs/product/` if it exists, for the buyer and the value metric hypothesis. If it
   does not exist, say so and offer `product-strategy` first.
2. List the cost drivers of one customer: variable ones (messages, storage, compute, support time) and fixed
   ones (base infrastructure). Find the measurement for each; read
   [references/model-structure.md](references/model-structure.md) for the file layout.
3. Fill the model file. Source every input or mark it as an assumption.
4. Run `python3 scripts/unit_economics.py model.json`. Fix every finding, read every warning.
5. Test the decision: what happens to margin if the top cost driver doubles, if conversion halves, if the
   biggest customer maxes out. Change the inputs and rerun.
6. Write the result and the open assumptions into `docs/product/pricing.md` with the model file next to it.
   Name what to measure to replace each assumption. Propose; the owner decides prices.

## Traps

- A limit that exists in the pricing page and not in the code.
- Annual price discounts computed before the payment fee.
- A free tier measured by sign-ups, not by cost per conversion.
- A "typical" usage figure taken from the average, hiding the few customers who cost most.
- Support time left out of the cost drivers.
- A price chosen to match a competitor with no cost model behind it.
- Currency and net/gross mixed in one model: the script assumes net amounts in one currency per month.

## Done when

- The model runs with no finding and each warning is explained.
- Every number has a source or is marked as an assumption, and the report says which results are estimates.
- Each plan shows typical and maximum-use margin, and the free tier shows cost per conversion.
- The open assumptions have a named measurement.
- Nothing was sent to customers and no price was changed in code; that waits for the owner.

## References

- [references/model-structure.md](references/model-structure.md): read when you create or edit the model file,
  or when a script finding needs interpreting.
- Run `python3 scripts/unit_economics.py --self-test` after changing the script.

## Sources

- https://www.willingnesstopay.com/saas-pricing-metrics: a pricing metric is the unit charged for; good ones
  align with value and with what customers expect to pay for. A vendor guide, verified 2026-10-31.
- The arithmetic rules need no external source; they operate on your own measurements. Legal terms (notice for
  price changes) and payment-provider fees come from `billing-eu-b2b` and the provider's own page and are
  recorded in the model as sourced inputs.
