# ADR template

Load this when a decision is settled and should outlive the plan: an answered open decision, a deviation from a
`[default]` rule, or a choice later plans will build on. Store ADRs in the project's decision folder (default
`docs/adr/NNNN-[slug].md`), numbered in order, never renumbered.

The sections follow Michael Nygard's original format: title, context, decision, status, consequences
(https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions, verified 2026-10).

```markdown
# NNNN. [Decision in a few words]

Status: Accepted
Date: [YYYY-MM-DD]
Decided by: [name]
Plan: [link to the plan that raised it, or none]

## Context
[The forces at play: the problem, the constraints, the options considered. Facts labeled verified or reported.]

## Decision
[What we do, in active voice: "We store credit notes in their own numbering sequence."]

## Consequences
[What becomes easier, what becomes harder, what we give up. For a deviation from a [default] rule, name the
trade-off that rule states and why it is acceptable here.]
```

- Superseding: write a new ADR, set the old one's status to "Superseded by NNNN", and link both ways.
- Keep it short. An ADR that needs more than a page usually holds two decisions.
