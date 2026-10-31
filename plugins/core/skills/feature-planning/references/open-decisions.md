# Open decisions

Load this when writing the plan's Open decisions section. These are the questions the owner answers before the
plan is approved.

## What belongs here

- Product: scope, which personas get it first, what the default behaviour is.
- Pricing and packaging: price points, billing units, which plans include it, limits.
- Legal: anything that changes contracts, notices, retention or processors.
- Hard-to-reverse architecture: a new data store, a public API shape, an identifier format, a vendor.

Choices that are cheap to change later and follow existing patterns don't belong here. Make them in the plan and
name the pattern you followed.

## Format

```markdown
## Open decisions
1. Should partial credit notes be possible in the first release?
   - Options: A, full credit notes only; B, full and partial.
   - Trade-offs: A ships a week earlier and needs no line-level UI; B avoids a second release that touches the
     same screens and tax logic. Both are reversible before customers depend on them.
   - Recommendation: B, because accountants correct single lines far more often than whole invoices, and the
     tax logic is the same.
2. ...
```

- One question per item, phrased so it can be answered with yes, no or a letter.
- Two to four options. Name them by letter so the owner can answer "1 B".
- Trade-offs on the axes that matter for this question: cost, reversibility, effort, risk, user impact.
- One recommendation with its reason. If you have no preference, say what would decide it.
- If there are no open decisions, write "None:" and why ("None: every choice follows existing ADRs, linked
  above").

## How to present them

- In the handover, repeat the numbered questions with their recommendations.
- Present the decisions as text the owner can discuss. Don't force them into a multiple-choice prompt.
- When the owner answers, update the plan, then record lasting decisions as ADRs.
