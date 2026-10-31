# Safe substitutes

Use these before asking for approval. Each one answers most "does it work" questions without reaching a real
person, a real account or production. Framework-specific helpers are in the framework's testing docs; this file
names the decision, not the syntax.

## Messages

| Instead of | Use | Check that it worked |
|---|---|---|
| A real SMS or push | The framework's notification fake in tests; a log or null transport in dev | The fake recorded the message with the expected recipient and body |
| Real email to customers | A local mail sink (an SMTP catcher with a web view) | The message appears in the sink, rendered |
| Real email in staging | A recipient interceptor that rewrites every recipient to a test address | The sink or test inbox shows the original recipient in a header |
| Chat or incident messages | A test channel or workspace owned by the team | The message lands in the test channel |
| Paging a person | The paging provider's test or sandbox mode, routed to yourself, with approval | Your own device rang; no one else's did |

Two wiring checks before anything notifies:

- List the transport of every channel in the current environment. A setup can send ordinary mail to the sink and
  still send one channel through a real provider.
- When the code picks a mailer or transport per message, that choice can override an environment-wide pin. Check
  the transport that is resolved at send time, not only the config file.

## Money

| Instead of | Use |
|---|---|
| A live payment API call | A mocked client with recorded fixtures; the provider's test mode with test keys |
| A live refund or payout | A test-mode refund; a unit test of the refund calculation |
| A live webhook from the provider | A recorded webhook body replayed against the local handler, with the signature computed from the test secret |

When the provider sends only IDs in webhooks, the fixture must include the follow-up fetch, mocked.

## Data

| Instead of | Use |
|---|---|
| Replaying a production record | A factory or seeder with anonymized values; take the structure from the stack trace or the schema, not the content |
| Running a query on production | The same query on seed data; for volume questions, `EXPLAIN` on a read replica, with read approval |
| Copying a production dump to a laptop | A generated dataset with the same shape and size class |

## Systems

| Instead of | Use |
|---|---|
| Triggering a failure on a real customer resource | A local target that fails on purpose |
| A deploy or infrastructure change | Plan, diff or dry-run output for review (for example `terraform plan`, `tofu plan`, `kubectl diff`, a server-side dry run) |
| A push | The commit range and the exact refspec, shown for review |
| A migration on a shared database | The migration on a local database, plus the SQL it will run |

## Seed data that fails on purpose

Seeded records built to fail (unreachable URLs, invalid cards, bouncing addresses) are picked up by every worker
that runs against that database. Before seeding them:

- Stop or isolate the workers that act on those records, or seed into a database no worker reads.
- Check where notifications go when the record's own contact is missing. The code may fall back to an account or
  owner address.
- Remove the records when the test ends.
