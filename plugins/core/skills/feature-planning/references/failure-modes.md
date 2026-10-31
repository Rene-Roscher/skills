# Failure modes

Load this when filling the failure-mode table. Each row names a failure, what the user or the business loses, how
you will notice, and what happens then. "We log it" is detection only if someone reads that log.

## Categories to cover

| Category | Example (booking system) | Questions |
|---|---|---|
| A dependency is down | The payment provider times out during checkout | Does the booking stay reserved? For how long? Who is told? |
| The feature's own component fails | The confirmation job crashes | Is the job retried? Does the guest get a confirmation twice, or never? |
| Partial data | Half the seats were imported when the import stopped | Can the import resume? Does the UI show a partial state honestly? |
| Retries and duplicates | The client retries a create request after a timeout | Is there an idempotency key? What happens on the second request? |
| Permission denied | A clerk without the refund permission opens the refund screen | Is the action hidden, disabled or refused server-side? What does the message say? |
| Limit reached | The organization hits its plan's booking limit mid-sale | Does the sale stop cleanly? Is the owner told before guests are turned away? |
| Bulk scale | An event with 5,000 bookings is cancelled at once | Do notifications go out in batches? Do queues for other work stall? |
| Concurrency | Two clerks book the last seat at the same time | Which one wins, and what does the other see? |
| Clock and time zones | A booking near midnight in another time zone | Which day is it stored on? Which day is shown? |
| Bad input from outside | A webhook arrives with an unknown event type | Is it stored, ignored or rejected? Does the sender retry forever? |

## Irreversible and costly effects

Below the table, list separately:

- What can't be undone: sent messages, charged cards, deleted data, published pages, external API calls with side
  effects.
- What costs money or reaches people if it fires wrongly: paid messages (SMS, voice), mass mail, paging, payouts,
  refunds.

For each, name the guard: a confirmation, a dry run, a rate limit, a kill switch, or a test-mode default.

## Writing good rows

- Impact in the user's terms: "the guest is charged but has no booking", not "500 error".
- Detection that exists or is part of the plan: an alert, a metric with a threshold, a reconciliation job.
- Reaction that a person can carry out at the stress moment, without reading the code.
