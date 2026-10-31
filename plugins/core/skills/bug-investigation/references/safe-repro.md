# Reproduce safely

## Substitutes per channel

The project's action matrix in `safe-actions` is the authority. Without one, use these:

| Channel | Instead of the real thing |
|---|---|
| Mail | The framework's mail fake in tests; a log or array transport; a local SMTP catcher in development |
| SMS, push, chat messages | A fake client that records messages; the provider's test credentials if it offers them |
| Payments | A mocked payment client in tests; the provider's test mode with test keys, never live keys |
| Outgoing webhooks | A local receiver, or a fake HTTP client that records requests |
| Paging and on-call | A fake notifier; never a test page to a real rotation without approval |
| Database | The local development database or a test database; a query plan on a replica, with approval |
| Third-party APIs | Recorded responses, or the vendor's sandbox |

Before running anything that might send: check which transport the environment actually uses. Configuration from
environment variables can point a "test" run at a real provider.

## Fixtures from the trace

- Read the frames and the event's data shape: which fields were set, which were null, which types.
- Build the fixture through the project's factories with invented values that have the same shape.
- Copying a production record brings personal data into tests, commits and logs. Rebuild the shape instead.
- Keep the fixture minimal: the fields that matter for the trigger, nothing else.

## Hard cases

- Time: freeze the clock at the moment from the event. Month ends, year ends, daylight-saving changes and time
  zones are common triggers.
- Races: make the interleaving deterministic. Use a fake that performs the competing write between the two steps
  of the code under test, or a barrier that holds one worker. Repeating the test until it fails proves little.
- Order and pagination: insert rows in the order that triggers the bug, and check that the query has an explicit
  order. Without one, the engine may return any order.
- Engine-specific behaviour: reproduce on the production engine (version from the project facts). An in-memory
  engine is a fast lane, not the proof.
- Workers and queues: run the job synchronously in the test, then once through the real queue locally.

## Reproduce as a test

1. Write the test with the fixture and the call that triggers the bug.
2. Run it and check that it fails for the reported reason, not for a setup error.
3. Name the trigger in one sentence: "[input or state] makes [code] do [wrong thing]".
