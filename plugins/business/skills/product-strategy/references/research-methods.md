# Research methods

Load this when collecting the evidence behind the brief. Each method ends in a fact you can label verified,
reported or inferred, with where it came from.

## Interviews about past behaviour

- Ask about the last time the problem happened: what triggered it, what they did, who else was involved, what it
  cost, what they tried before.
- Don't pitch and don't ask whether they would use or pay for something. Hypothetical answers are polite, not
  predictive.
- Ask who signs off on a purchase and who would object. That separates buyer, user and blocker.
- Write notes the same day, with the date and the role (not the name) of the person. Quotes stay verbatim.
- Interview each persona separately. Stop when new interviews add no new workaround, cost or objection.

## Existing data

Before interviewing, read what the business already has:

- Support tickets and their tags: what people could not do, in their own words.
- Sales notes and lost deals: the reason given, and the alternative they chose.
- Cancellation reasons and churned accounts.
- Usage from the system of record: which capabilities active accounts use, and which paid accounts use that free
  accounts don't.
- Upgrade attempts: count them by the gated screen they started from. That shows which capability people reach
  for when they hit a limit.

Data from production systems may hold personal data. Query aggregates, read only, and follow
`gdpr-engineering` for anything stored outside the system.

## Competitor scan

1. List alternatives in three kinds: the workaround (spreadsheet, manual process, doing nothing, an agency),
   direct competitors, and adjacent tools that customers stretch to cover the job.
2. For each direct and adjacent alternative, read its pricing page, plan comparison, documentation and changelog
   now. Record the URL, the date, the region and language of the page, and the claim in its own words.
3. A claim you could not read today is marked unverified. A remembered price is not a source.
4. Read reviews and community threads for complaints, and label them reported: they are opinions of single users.
5. Note what the entry plan of each alternative includes. This feeds the table-stakes matrix.

## Table-stakes matrix

| Capability | Alt A entry plan | Alt B entry plan | Workaround | Ours |
|---|---|---|---|---|
| Shared calendar | yes (URL, date) | yes (URL, date) | partly | planned |
| Client deadline view | no | no | no | yes |

- A capability present on every relevant entry plan is table stakes: customers expect it as standard.
- A capability present nowhere else but valued in interviews is a candidate differentiator.
- A capability present nowhere and never mentioned in interviews is a guess. Put it in assumptions.

## Funnel count

Count each step for the same period from the system of record: visits (analytics), signups, activation (the
first action that delivers the job), first payment, renewal. Record both analytics and database counts where
they overlap, and the gap between them. The success metric belongs to the step that loses the most people, not
to the step that is easiest to raise.

## Positioning workshop

Answer the five questions in order, in writing, with evidence next to each answer:

1. Competitive alternatives: from the alternatives table, workaround first.
2. Differentiated capabilities: rows of the matrix where only "Ours" says yes.
3. Value: what each capability lets the customer do, in interview language.
4. Best-fit customers: characteristics shared by the people who cared most in interviews and data.
5. Market category: the frame in which that value is obvious to them.

If step 2 is empty, the product has no position yet. Record that as an open decision, not as copy.
