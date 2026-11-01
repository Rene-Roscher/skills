---
name: product-strategy
description: "Frames a product before it is built: problem without a solution, buyer versus user, jobs and today's workaround, the highest-stress moment, alternatives and table stakes, positioning, success metric, non-goals and assumptions to test, written to docs/product/. Use when shaping a product, segment or positioning, or asking who buys and why. Not for feature plans or pricing."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Product strategy

This skill writes down what a product is for before features are planned: who has the problem, what they do
today, who pays, what they already expect as standard, why they would switch, and how success is measured. The
result is a small set of files in `docs/product/` that `feature-planning` links for every feature and that
`pricing-and-unit-economics` reads for the value metric. It prevents a well-built product for a buyer nobody
checked, and a product that competes on features every alternative already includes.

## Applies when / does not apply

- Applies: a new product or product line, a new customer segment or market, repositioning, a product brief,
  vision document or Lean Canvas, "who is this for", "who are our competitors", "how do we position this",
  "what should we measure", "what do customers expect as standard", and the start of a roadmap.
- Does not apply: planning one feature's implementation (`feature-planning`), prices, plans and limits
  (`pricing-and-unit-economics`), checkout, tax and invoices (`billing-eu-b2b`), page or mail copy, and checking a
  library or API fact (`evidence-before-claims`).

## Rules

Most important first. Examples use a project tool for small architecture offices.

- [invariant] Problem first, with no solution in it. Write who has the problem, in which situation, what they do
  today and what it costs them (time, errors, money, risk). No product name, feature, screen or technology in this
  section. Why: a problem stated as a solution ("they need a dashboard") can't be compared with the alternatives
  and fixes the design before the need is known. Test: `check_brief.py` reports B03 when the Problem section
  names the product or a word from the solution list. Source: Christensen Institute, Jobs to Be Done: "People
  don't simply buy or pick products or services; they pull them into their lives to make progress."
  (https://www.christenseninstitute.org/theory/jobs-to-be-done/, verified 2026-10-31).
- [invariant] Name the buyer and the user separately, each with what they judge and what makes them say no. Add
  the admin who configures it and the outside person who sees the result, where they exist. When one person is
  both buyer and user, write that down. Why: in B2B the person who signs often never uses the product, so proof
  that users like it is not proof that anyone pays, and the reverse. Test: B04 when Personas has no `Buyer:` or no
  `User:` line. Source: SVPG, "Four big risks": value risk is "whether customers will buy it or users will choose
  to use it" (https://www.svpg.com/four-big-risks/, verified 2026-10-31).
- [invariant] Write each persona's job as progress in a circumstance, with its functional, social and emotional
  part, and write today's workaround next to it, including doing nothing, a spreadsheet, a manual process or a
  person hired for it. The workaround is the first competitor. Why: customers compare a new product with what
  they do now, not with the market leader's feature list. Test: B05 when Jobs has no `Today:` line. Source:
  Christensen Institute: "the progress they're trying to make as they strive toward a goal or aspiration within
  particular circumstances" and "All Jobs incorporate functional, social, and emotional forces"; April Dunford:
  "the customer would stick with their current way of solving the problem"
  (https://www.aprildunford.com/post/a-quickstart-guide-to-positioning); both verified 2026-10-31.
- [invariant] Name the moment of highest stress in which the product is used, and what each persona needs in it:
  speed, clarity, the right permission, volume, a way to undo. For the project tool it is the day before a client
  deadline, with five people editing. Why: B2B customers judge a product in that moment, and a brief that covers
  only the calm path sends every feature plan in the wrong direction. Test: B01 or B02 when the Stress moment
  section is missing or empty. Source: reproducible with the test; `feature-planning` uses the same field per
  feature.
- [invariant] Every claim about an alternative (a feature, a plan limit, a price, an integration) carries the URL
  it came from and the date it was read. A claim without both is marked unverified and does not decide anything.
  Why: pricing pages and plan contents change, and a remembered claim often describes an older version. Test: B07
  on an Alternatives row without an https URL and a `YYYY-MM-DD` date that is not marked unverified. Source:
  reproducible with the test; the checking method is in `evidence-before-claims`.
- [invariant] One success metric with `Baseline:`, `Target:`, `By:` and `Source:`, where the source is the query
  or report that produces it. Count signups, activations and payments from the system of record (database,
  billing) and use web analytics only for what happens before signup. Why: analytics scripts do not run for
  visitors who block them or decline consent, so analytics counts of signups and payments run below the
  database, and a target set on them misreads progress. Test: B06 when a field is missing; then count last month's
  signups in both sources and record the gap in the metric's notes. Source: reproducible with that comparison;
  Lean Canvas "Key Metrics": "The numbers that tell you how your business is doing"
  (https://leanspark.ai/leancanvas, the current home of the LEANSTACK canvas, verified 2026-10-31).
- [invariant] Write the non-goals, starting with what a reader would assume is included. Why: unstated scope
  comes back in every feature plan as "we also need". Test: B01 or B02 when Non-goals is missing or empty.
  Source: reproducible with the test.
- [invariant] List the assumptions before building. Each has one of the four risks (value, usability,
  feasibility, business viability), the cheapest test that could prove it wrong, a pass threshold written before
  the test runs, and a date. Test value and viability first. Why: a threshold set after the result always fits the
  result, and the expensive surprises are "nobody pays" and "it can't make money". Test: B08 when an item lacks
  `Risk:`, `Test:`, `Threshold:` or `By:`. Source: SVPG: "Tackle the big risks early – especially value risk and
  business risk" (https://www.svpg.com/four-big-risks/, verified 2026-10-31).
- [invariant] Strategy choices belong to the owner: target segment, positioning, market category, scope cuts.
  Collect them as numbered open decisions, each with options, trade-offs and one recommendation, in the format
  of `feature-planning`, and stop for an answer. Test: B09 when Open decisions is not numbered or an item has no
  `Recommendation:`. Source: reproducible with the test.
- [default] Table stakes: list what every relevant alternative includes on its entry plan. Customers expect these
  as standard. Ship them, don't gate them behind a higher plan unless cost forces it (then say so in an ADR), and
  don't present them as the differentiator. Trade-off: table stakes take build time and may cost money on free
  plans, before they win any deal. Deviate only with an ADR that names this trade-off. Source: Dunford's
  differentiation question, "What do we have that the alternatives do not?", which a feature every alternative
  has cannot answer; Kano et al. 1984 separate "must-be" from "attractive" and "one-dimensional" quality
  (https://doi.org/10.20684/quality.14.2_147); both verified 2026-10-31.
- [default] Position in April Dunford's order: competitive alternatives, then the capabilities they lack, then the
  value those capabilities enable, then the customers who care a lot about that value, then the market category
  in which the value is obvious. Write five short answers before any tagline. Trade-off: it needs research on the
  alternatives before any copy exists. Deviate only with an ADR that names this trade-off. Source: Dunford: "We
  start with competitive alternatives" and "Lastly, we move to market category"
  (https://www.aprildunford.com/post/a-quickstart-guide-to-positioning, verified 2026-10-31).
- [default] Name a first segment narrow enough that you can list real organisations in it, and write what makes
  them care more than others. Trade-off: messaging excludes customers who might also buy. Deviate only with an ADR
  that names this trade-off. Source: Lean Canvas "Early Adopters": "The specific subset of customers you target
  first" (https://leanspark.ai/leancanvas, verified 2026-10-31).
- [default] The files land in `docs/product/`: `brief.md` (problem, personas, jobs, stress moment, success metric,
  non-goals), `market.md` (alternatives, table stakes), `positioning.md`, `assumptions.md`, plus open decisions in
  the brief. Settled decisions become ADRs (template in `feature-planning`). Feature plans link the brief instead
  of restating it. Trade-off: several files to keep current; a small product may keep the same headings in one
  file. Deviate only with an ADR that names this trade-off. Proof: `check_brief.py docs/product` passes on either
  layout.

## Procedure

1. Gate: if `docs/product/` exists, read it and update it instead of starting over. If the request is one
   feature, hand over to `feature-planning` and link the brief.
2. Collect evidence: interview notes, support tickets, sales and lost-deal notes, churn reasons, usage and
   upgrade events from the system of record. Label each fact verified, reported or inferred. Methods:
   [references/research-methods.md](references/research-methods.md).
3. Write the problem, personas, jobs with today's workaround, and the stress moment.
4. Build the alternatives table: the workaround, direct competitors, adjacent tools. Read each source now and
   date it. Derive the table stakes.
5. Answer the five positioning questions in order.
6. Write the success metric, the non-goals, and the assumptions with their tests and thresholds.
7. Write the files from [references/brief-template.md](references/brief-template.md) and run
   `python3 ${CLAUDE_SKILL_DIR}/scripts/check_brief.py docs/product --product-name [name]`. In clients that don't
   set `CLAUDE_SKILL_DIR`, the script is in this skill's `scripts/` folder. Fix every finding.
8. Gate: present the path, the problem in two sentences, the five positioning answers, the riskiest assumption
   with its test, and the numbered decisions. Stop until the owner answers.

## Traps

- "Would you use this?" measures politeness. Ask what the person did the last time the problem happened, and
  what it cost.
- Paying customers and active free users can want different things. Check what the paying ones bought and why
  before ranking requests by count.
- A healthy signup curve can hide that almost nobody pays. Count each step from visit to paid in the system of
  record and pick the metric at the step that loses the most people.
- A competitor list from memory, or from the market leader alone, misses the spreadsheet and the manual process
  that most prospects use.
- Copy that sells a table-stakes feature as unique reads as unaware of the market to buyers who compared.
- "Everyone in the industry" as the target segment means no first segment was chosen.
- A metric that counts output ("features shipped", "pages published") says nothing about the problem.
- Competitor pages in another language or region often show different plans and prices. Record which page was
  read.

## Done when

- `docs/product/` holds the brief, market, positioning and assumptions sections, and `check_brief.py` exits 0.
- Every alternative row has a source URL and read date, or is marked unverified.
- The success metric names its query or report and comes from the system of record.
- Each assumption has a risk type, a test, a threshold and a date.
- The owner has the numbered decisions with recommendations, and nothing was built.

## References

- [references/brief-template.md](references/brief-template.md): load when writing or restructuring the files in
  `docs/product/`; it holds the headings and field lines the checker expects.
- [references/research-methods.md](references/research-methods.md): load when collecting evidence: interviews
  about past behaviour, mining support and sales data, the competitor scan, the table-stakes matrix and the funnel
  count.
- `${CLAUDE_SKILL_DIR}/scripts/check_brief.py`: run on `docs/product/` before handover. `--help` lists the checks
  B01 to B09; `--self-test` runs its fixtures.

## Sources

- https://www.christenseninstitute.org/theory/jobs-to-be-done/: jobs as progress in circumstances, functional,
  social and emotional forces, verified 2026-10-31.
- https://www.aprildunford.com/post/a-quickstart-guide-to-positioning: five positioning components, their order,
  "do nothing" as an alternative, verified 2026-10-31.
- https://leanspark.ai/leancanvas: Lean Canvas boxes including Existing Alternatives, Early Adopters and Key
  Metrics (the LEANSTACK URL redirects here), verified 2026-10-31.
- https://www.svpg.com/four-big-risks/: value, usability, feasibility and business viability risk, tackle value
  and business risk early, verified 2026-10-31.
- https://doi.org/10.20684/quality.14.2_147: Kano, Seraku, Takahashi, Tsuji, "Attractive Quality and Must-Be
  Quality", 1984, quality categories, verified 2026-10-31.
