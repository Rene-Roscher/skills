# Self-review

Load this before handing the plan over. Answer each question in the plan's Self-review section with a fact or a
number. "Should be fine" is not an answer.

## The fixed questions

1. Does the data model hold at peak volume? Give the numbers: rows per day, largest tenant, index used by each
   query.
2. What does the user see when each part fails? Point to the failure-mode rows.
3. Can one tenant see or change another tenant's data on any surface? Name the surfaces you checked.
4. What does one operation cost in queries, scans, jobs and paid messages? And at bulk scale?
5. How do we roll back two hours after release in production, including data written since?
6. What must the customer learn, and where is it documented (help page, changelog, API reference)?
7. Is the lifecycle complete: create, edit, correct, withdraw, restore, without duplicates on retry?
8. Which facts in the plan are not verified, and does any decision rest on one of them?
9. Does the plan add a second mechanism where an existing one could take a new axis?
10. Is every comparison with other products ("simpler than", "faster than") checked against the lifecycle
    questions above?

## Adversarial review for critical plans

Plans that touch money, authentication, authorization, tenant isolation or concurrency get exactly one adversarial
review before handover.

- The reviewer sees the plan and the code, not the conversation that produced the plan.
- The brief is to find what breaks: wrong assumptions, missing failure modes, leaks, double charges, races.
- Check each finding yourself before changing the plan. Findings are leads, not facts.
- Record in the Self-review section what the review found and what changed. Rejected findings get a one-line
  reason.
