# Brief template

Load this when writing or restructuring `docs/product/`. The headings and the `Field:` lines are what
`check_brief.py` reads. Heading level doesn't matter; the text does. The files may be merged into one for a small
product. Replace every bracketed hint.

## Contents

- docs/product/brief.md: problem, personas, jobs, stress moment, success metric, non-goals, open decisions
- docs/product/market.md: alternatives, table stakes
- docs/product/positioning.md: competitive alternatives, differentiated capabilities, value, best-fit customers, category
- docs/product/assumptions.md: assumptions with a test each
- Hand-checks without Python

## docs/product/brief.md

```markdown
# [Product] brief

Status: Draft
Owner: [name]
Updated: [YYYY-MM-DD]

## Problem
[Who, in which situation, what they do today, what it costs them. No product name, feature or technology.]

## Personas
Buyer: [role], judges [cost, risk, what their boss asks], says no when [reason].
User: [role], judges [speed, fewer errors], says no when [reason].
Admin: [role, or "same as user"].
Outside: [person who sees the result, or "none"].

## Jobs
[Persona]: [the progress they want, in which circumstance]. Functional: [...]. Social: [...]. Emotional: [...].
Today: [the workaround, including doing nothing], costing [time, errors, money].

## Stress moment
[The moment of highest stress.] [What each persona needs in it.]

## Success metric
Metric: [what is counted].
Baseline: [measured value with date, or "not measured yet"].
Target: [value].
By: [YYYY-MM-DD]
Source: [query, report or table that produces it].

## Non-goals
[What this product does not do, starting with what a reader would assume.]

## Open decisions
1. [Question answerable with yes, no or a letter.]
   - Options: A, [...]; B, [...].
   - Trade-offs: [...].
   - Recommendation: [letter], because [...].
```

## docs/product/market.md

```markdown
# Market

## Alternatives
| Alternative | Kind | Claim | Source | Read |
|---|---|---|---|---|
| Spreadsheet and group chat | workaround | free, no deadline view | interview notes | 2026-09-12 https://example.com/notes/7 |
| [Vendor] | direct | [feature, limit or price as stated] | https://[vendor page] | [YYYY-MM-DD] |
| [Vendor] | adjacent | [claim] | unverified, [why] | |

## Table stakes
[Capabilities every relevant alternative includes on its entry plan. One line each, with the rows that show it.]
```

`Kind` is workaround, direct or adjacent. The workaround rows come from interviews and tickets, not from vendor
pages.

## docs/product/positioning.md

```markdown
# Positioning

## Competitive alternatives
[What customers would do if the product did not exist.]

## Differentiated capabilities
[What the product has that those alternatives do not.]

## Value
[What those capabilities let the customer do, in their terms, with proof where it exists.]

## Best-fit customers
[Characteristics of the customers who care a lot about that value. Real organisations that fit.]

## Market category
[The context in which that value is obvious to those customers.]
```

## docs/product/assumptions.md

```markdown
# Assumptions

1. [Assumption as a falsifiable sentence.] Risk: value. Test: [cheapest test that could prove it wrong].
   Threshold: [pass condition, set before the test]. By: [YYYY-MM-DD]. Result: [filled after the test].
2. ...
```

Risk is one of value, usability, feasibility, viability. Record results in place and keep failed assumptions:
they explain later decisions.

## Hand-checks without Python

- Problem has no product name, feature or technology.
- Buyer and User lines both exist.
- Every job has a Today line.
- The metric has Baseline, Target, By and Source.
- Every alternatives row has a URL and a date, or says unverified.
- Every assumption has Risk, Test, Threshold and By.
- Open decisions are numbered and each has a Recommendation.
