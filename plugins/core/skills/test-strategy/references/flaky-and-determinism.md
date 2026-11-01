# Flaky tests and determinism

Load when a test fails intermittently, or when you write tests that touch time, randomness, queues or shared
state.

## Decide the same day

An intermittent failure gets one of two outcomes within the working day:

1. Fixed, with the cause named in the commit message.
2. Quarantined: moved out of the required suite into a separate suite that still runs and reports, with an
   owner and a deadline in the tracker.

A quarantine without a limit rots. Pick a mechanism: a maximum count (for example, at most a small fixed
number of quarantined tests; at the limit, stop feature work and clear them), a deadline per test that fails
the build when it passes, or both. The Fowler article lists the count limit among the mechanisms it has seen.
After the deadline the test is fixed or deleted. A deleted test needs a note on which behaviour is now
unprotected.

Automatic reruns are acceptable only as a measurement: rerun to find out that a test is flaky, then handle it as
above. A rerun that turns red into green without a record hides the product races the Google report says are
among the causes (concurrency, undefined behaviour, flaky third-party code, infrastructure).

## Find the cause

| Symptom | Likely cause | Fix |
|---|---|---|
| Passes alone, fails in the full run | shared state: database rows, files, globals, a frozen clock not reset | isolate per test; reset in teardown; randomise order to expose it |
| Fails near midnight, month end or a DST change | real clock | inject a clock; freeze it in the test |
| Fails under load, passes locally | fixed sleep too short | wait for a signal, or poll with a deadline |
| Fails once in many runs, no pattern | race in the product or the test | run the test in a loop with logging; check for unawaited async work |
| Fails when the network is slow | real call to a third party | fake it, and contract-test the fake |
| Ordering differs between runs | query without a sort, hash ordering | sort in the query, or compare as sets |

Source for the table's time, sleep, remote-service and isolation rows:
https://martinfowler.com/articles/nonDeterminism.html (verified 2026-11-01).

## Waiting

- Prefer a completion signal: await the promise, join the thread, drain the queue synchronously in the test, or
  wait on a visible state change.
- If you must poll, give it a deadline and a short interval, and fail with a message that names what was
  awaited.
- A fixed sleep appears in a test only with a comment that says why no signal exists.

## Time

- Production code receives a clock (a parameter or a service). Tests pass a clock set to a fixed instant.
- Test the boundaries: just before and after midnight in the business time zone, month end, a leap day, and the
  DST switch days if the code schedules by local time.
- Reset the frozen clock after each test.

## Randomness and ordering

- Seed every generator the test uses. Print the seed on failure so a run can be replayed.
- Property-based tools keep failing examples; commit the failing case as a plain example test.
- Run the suite in random order now and then. A test that depends on another one fails there first.

## Shared state

- Each test creates what it needs through a builder and cleans up, or runs inside a transaction that rolls back
  when the engine allows it.
- No test reads data another test wrote. No test depends on the seeded rows of a development database.
