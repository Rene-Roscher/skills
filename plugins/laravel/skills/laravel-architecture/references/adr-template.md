# ADR template

Load when deviating from a `[default]` rule. An `[invariant]` has no ADR route; report the conflict instead.

Store ADRs where the project keeps them, for example `docs/adr/NNNN-[slug].md`, numbered in order.

```markdown
# NNNN: [decision in a few words]

Status: proposed | accepted | superseded by NNNN
Date: YYYY-MM-DD
Rule: [skill name] / [the [default] rule, quoted in one line]

## Context
What forces the deviation. Facts with sources: versions, measurements, constraints.

## Decision
What we do instead, in one or two sentences.

## Trade-off
The trade-off the rule names, and how this decision lands on it. What we give up, what we gain.

## Consequences
Tests, guards or allowlist entries that change. What would make us revisit this.
```

Rules for the ADR itself:

- The trade-off section quotes the rule's own `Trade-off:` line and answers it. An ADR that skips it is
  incomplete.
- Link the ADR from every allowlist entry or `ignoring()` call it justifies.
- A superseded ADR stays in place with a pointer to its successor.
