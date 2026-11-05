---
name: test-strategy
description: "Decides what to test and how tests carry weight: critical paths (money, auth, tenant isolation, deletion, permissions) first, each test seen failing, assertions on outcomes not mocks, no weakened assertions, flaky tests as bugs, coverage gates on critical modules, spike load tests. Use when planning, writing or reviewing tests or a coverage target. Not for proving a fix works (verify-before-done)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Test strategy

This skill decides which tests a change needs, at which level, and which numbers may gate a merge. It leaves test
frameworks, runner flags and CI syntax to their vendors' docs, and it leaves the question "is this item done"
to `verify-before-done`. When an agent writes most of the code, the test suite is the main reviewer, so every
test has to be able to fail for the right reason. The failure it prevents: a large suite and a high coverage
number that still let a broken refund, a leaked tenant row or a missing permission check reach production.

## Applies when / does not apply

- Applies: you plan tests for a feature or a bug fix, decide where a new test belongs, review a test suite or a
  pull request's tests, set or argue about a coverage target, handle a test that fails intermittently, or plan a
  load test for a service that must absorb traffic spikes.
- Does not apply: proving that a change works in a running system, red-green proof of a regression test and
  test-versus-production gaps (`verify-before-done`); planning a feature (`feature-planning`); reproducing a
  defect (`bug-investigation`); the technique of browser checks (`browser-verification`, plugin web).

## Rules

- [invariant] Every critical path has tests for the allowed case and for the refused case: money (amounts,
  rounding, refunds, currency), authentication, tenant isolation, data deletion, and permissions. Why: these are
  the paths where one missed branch means a loss, a leak or a legal problem, and a happy-path test cannot see a
  missing check. Test: remove the tenant filter, the permission check or the refund cap from the code under
  test; at least one test goes red. If all stay green, the path has a gap. Source: none; design judgment,
  consistent with https://testing.googleblog.com/2020/08/code-coverage-best-practices.html ("what's not
  covered is more meaningful than what is covered", verified 2026-11-01).
- [invariant] Tests assert observable behaviour: the return value, the response, the stored row, the sent
  message. They do not assert which internal methods ran or in which order. Why: tests tied to the structure
  break on every refactor and stop being a safety net. Test: rename a private method or split a class without
  changing behaviour; no test fails. Change the behaviour; a test fails. Source:
  https://martinfowler.com/articles/practical-test-pyramid.html ("Test for observable behaviour instead",
  verified 2026-11-01).
- [invariant] Every new test has been seen failing against broken code before it counts: run it before the
  fix or the feature exists, or break the code under test on purpose, see it red for the expected reason, then
  restore. This applies to every new test, not only regression tests; the red-green record for a bug fix is
  in `verify-before-done`. For behaviour that depends on the environment (transport security, transactions,
  timing and waits, file locks, signals), first prove by hand that the test environment can produce the
  failure at all, then encode that proof as the test: a header that is only sent over HTTPS cannot be asserted
  over plain HTTP, a statement that refuses to run inside a transaction cannot be tested inside the test's
  wrapping transaction, and a wait that returns at once proves nothing about the timeout. Why: a test that was
  never red may be unable to fail, and a suite of such tests approves any change. Test: revert the change the test was written for; the test fails with an assertion
  message about the behaviour, not with an import or setup error. Source:
  https://newsletter.kentbeck.com/p/canon-tdd (a failing test comes before the code change; verified
  2026-11-03).
- [invariant] Assert what the code produced, not what the test arranged. A stub that returns a value followed
  by an assertion on that same value checks the stub. An assertion that a mock was called with the arguments
  the test itself passed in checks the wiring of the test. Assert the state, the response, the persisted rows
  or the emitted events instead. Assert on a call only where the call is the outcome (a charge, a sent
  message, a published event), and then check the payload the code built. Why: interaction assertions cannot
  show that the system works, only that functions were called. Test: replace the body of the function under
  test with a pass-through to its collaborator; a test that still passes asserts the arrangement. Source:
  https://abseil.io/resources/swe-book/html/ch13.html (prefer state testing; interaction testing "can't tell
  you that the system under test is working properly"; verified 2026-11-03).
- [invariant] Every test has an assertion the code under test can fail. No test that only checks the call
  returns without an exception, no `assert(true)` or empty test body, no snapshot of a whole page, response or
  object graph standing in for named expectations; a snapshot stays small and focused on the part the test is
  about. Why: such tests raise coverage and pass for almost any implementation. Test: change the computed
  value in the code under test (a total, a status, a field); a test fails. Source:
  https://newsletter.kentbeck.com/p/canon-tdd ("write tests without assertions just to get code coverage" is
  named a mistake) and https://jestjs.io/docs/snapshot-testing (keep snapshots focused and short; fight the
  habit of regenerating snapshots instead of examining the failure), verified 2026-11-03.
- [invariant] Never delete, loosen or skip an assertion to make a run green: no removed checks, no widened
  tolerance, no expected value replaced with whatever the code now returns, no added skip marker, no
  regenerated snapshot without reading the diff. If a test fails and the behaviour change was not asked for,
  stop and report the failing test, the expected and actual values, and your reading of which side is wrong.
  If the change was asked for, update the assertion to the new requirement and say so in the report. Why: a
  weakened assertion turns the reviewer off for exactly the change it should catch. Test: hand the agent a
  task whose correct fix makes an existing test fail; the diff keeps or tightens that assertion, or the reply
  reports the conflict. Source: https://newsletter.kentbeck.com/p/canon-tdd ("delete assertions so the test
  pretends to pass" and copying computed values into expected values are named mistakes; verified 2026-11-03).
- [invariant] Tests are deterministic. Time comes from an injectable clock that the test freezes, randomness from
  a seed the test sets, and waiting for asynchronous work uses an explicit signal or a bounded poll with a
  deadline, never a fixed sleep. Why: a sleep is either too long and slows the suite or too short and flakes
  under load; real clocks make results differ by the minute. Test: run the test 20 times, once with the system
  clock set across midnight and a month end; every run gives the same result. Source:
  https://martinfowler.com/articles/nonDeterminism.html (sleep and system clock sections, verified 2026-11-01).
- [invariant] End-to-end and browser suites start from an isolated, clean state on every run: their own
  database, their own ports, their own build output, and caches, queues, sessions and rate-limit counters reset
  in the global setup. Limits the suite can exhaust (requests per hour, sign-ups per address) are configurable
  and set for the test run. The suite never uses or changes the developer's database, dev server, ports or dev
  build files. Why: state left by an earlier run (a counter that survives in a cache table, a row another test
  created) turns a green test red in the full run only, and a suite that shares the dev setup damages it. Test:
  run the full suite twice in a row and once while the dev stack runs; all three runs give the same result and
  the dev database is unchanged. Source: none; design judgment. Technique in `browser-verification`.
- [invariant] A flaky test is a bug, in the test or in the product, and it gets a decision the same day: fix it,
  or quarantine it with a named owner and a deadline. A quarantined test leaves the required suite, stays
  visible, and is fixed or deleted by the deadline. Silent automatic reruns do not count as a decision. Why:
  one report found about 1.5% of all test runs flaky and about 84% of pass-to-fail transitions involving a flaky
  test, so people learn to ignore red builds. Test: a test that fails 1 run in 20 is not in the required suite
  by the end of the day and has an owner and a date in the tracker; after the date it is fixed or deleted.
  Source: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html and
  https://martinfowler.com/articles/nonDeterminism.html (quarantine, "fix quarantined tests quickly", a
  mechanism so tests do not stay long), verified 2026-11-01.
- [default] Gate on coverage of critical modules and of changed lines. Do not gate on one global percentage.
  Read coverage as a map of what no test executes, not as proof that executed code is checked. Trade-off:
  per-path thresholds need configuration and an agreed list of critical modules, and a global dashboard number
  is easier to explain. Deviate only with an ADR that names this trade-off. Source:
  https://testing.googleblog.com/2020/08/code-coverage-best-practices.html (no universal ideal number; coverage
  shows execution, not correct assertion; per-commit goals; its own 60, 75 and 90 percent guidelines are
  not mandated top-down), verified 2026-11-01.
- [default] Shape the suite by where the risk sits. Start from the pyramid: many fast tests on logic, fewer on
  integration points, very few end to end. Move toward the trophy (more integration tests that run real
  components together, less isolated unit testing) when most of the code is glue between a framework, a
  database and a UI. Push each test as far down as it can still fail for the right reason. Trade-off: the
  pyramid gives speed and precise failures but can pass while the parts do not fit; the trophy gives
  confidence in the wiring but slower runs and coarser failures. Deviate only with an ADR that names this
  trade-off. Source: https://martinfowler.com/articles/practical-test-pyramid.html (rule of thumb, "push your
  tests as far down the test pyramid as you can"), https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications
  (trophy; meant for one codebase; the author calls the percentage debate a distraction), verified 2026-11-01.
- [default] Cover the few journeys that must never break (sign-up, login, checkout or the equivalent) with
  end-to-end tests in a real browser, and keep that set small. When an end-to-end test finds a bug that no
  lower test caught, add the lower test. The browser technique is in `browser-verification`. Trade-off: these
  tests are slow and the most prone to flakiness (timing, animations, pop-ups), and a small set leaves
  edge cases to lower levels. Deviate only with an ADR that names this trade-off. Source:
  https://martinfowler.com/articles/practical-test-pyramid.html (end-to-end tests are "notoriously flaky";
  write a lower-level test when a higher one finds an error), verified 2026-11-01.
- [default] At every boundary to another team's service or a third party, run a contract test against the
  fake and, where possible, against the real service or its test instance, so the fake cannot drift. Trade-off:
  more setup and a place to keep the contract files; a plain stub is cheaper and goes stale silently. Deviate
  only with an ADR that names this trade-off. Source: https://martinfowler.com/articles/practical-test-pyramid.html
  (contract tests against the fake and the real server keep the fake a faithful test double), verified
  2026-11-01.
- [default] Use property-based tests where the input space is large and the rule is stated as a property
  (a sort keeps its elements, an encode-then-decode returns the input, a total never goes negative). Keep the
  example tests that name known edge cases. Trade-off: properties are harder to write and failures need
  shrinking to read; example tests are clearer but only cover inputs someone thought of. Deviate only with an
  ADR that names this trade-off. Source: https://hypothesis.readthedocs.io/en/latest/ (tests that should pass
  for all inputs in a described range, random inputs including edge cases, verified 2026-11-01).
- [default] Run mutation testing on the critical modules, on a schedule rather than on every commit, and treat
  surviving mutants as missing assertions. Trade-off: it multiplies test run time, so it is scoped to the few
  modules where an unchecked line is expensive. Deviate only with an ADR that names this trade-off. Source:
  https://stryker-mutator.io/docs/ (mutants inserted into production code; a mutant that survives means the
  tests did not fail), https://testing.googleblog.com/2020/08/code-coverage-best-practices.html (mutation
  testing as the better check that covered lines are asserted), verified 2026-11-01.
- [default] Build test data with builders or factories: one function returns a valid default object and the
  test overrides only the fields it is about. Do not copy large literals between tests or depend on a shared
  seeded database that every test mutates. Trade-off: builders are code to maintain and can hide what makes a
  case special if the overrides are not visible in the test. Deviate only with an ADR that names this
  trade-off. Source: none; design judgment.
- [default] Name a test for the behaviour and the condition ("refund above paid amount is rejected"), and build
  it as arrange, act, assert with one reason to fail. A name such as "works", "test process" or "handles the
  case" says nothing when the test goes red, so it fails review. Trade-off: long names and more small tests instead of one
  large scenario. Deviate only with an ADR that names this trade-off. Source:
  https://martinfowler.com/articles/practical-test-pyramid.html (arrange, act, assert; given, when, then),
  verified 2026-11-01.
- [default] For a service that must absorb traffic spikes, plan a spike test next to the average-load test.
  State the question first: does the service keep its latency and error limits when traffic jumps to several
  times the average within seconds, and does it return to normal after the spike? Write the limits before the
  run, aim at a production-like environment you own, and never at someone else's service. Trade-off: a
  realistic environment and traffic model cost time and money, and a smaller environment gives numbers that do
  not scale. Deviate only with an ADR that names this trade-off. Source:
  https://grafana.com/docs/k6/latest/testing-guides/test-types/ and
  https://grafana.com/docs/k6/latest/testing-guides/test-types/spike-testing/ (spike test: sudden and massive
  rushes, very high load, no or very short plateau; no single test type removes all risk; k6 is one example
  tool), verified 2026-11-01.

## Procedure

1. List the behaviours the change touches and mark each with impact and how often it changes. Mark the critical
   paths. Read [references/risk-and-coverage.md](references/risk-and-coverage.md) for the map and the gate.
2. For each behaviour, pick the lowest level at which a test can fail for the right reason. Add an integration
   test where data is read or written across a boundary.
3. Write the tests with builders, a frozen clock and a seeded generator. Name each after its behaviour.
   Assert outcomes, and see each new test fail against broken code before you rely on it.
4. Run the critical-path check: break the guard on purpose and see a test fail. Then restore it. The red-green
   proof for a regression test itself belongs to `verify-before-done`.
5. Add contract tests at each boundary that has a fake. Add or update the few browser journeys last.
6. Set the gates: coverage on critical modules and changed lines, a quarantine suite with a count limit and a
   deadline per test, mutation runs on the critical modules.
7. If traffic spikes matter, plan the load and spike tests. Read
   [references/load-and-spike.md](references/load-and-spike.md) for the questions and the design.
8. For an intermittent failure, read [references/flaky-and-determinism.md](references/flaky-and-determinism.md)
   before adding a retry.

## Traps

- A coverage report that counts lines executed by a test with no assertion. The number rises and nothing is
  checked.
- A mock that repeats the production code line by line. The test passes when the code is wrong in the same way.
- A fake third-party service written once and never compared with the real one. The provider changes a field and
  every test stays green.
- A retry plugin that makes the build green and hides a race in the product.
- Tests that share one database state and pass only in file order.
- Getter and setter tests written to move a percentage. They add maintenance and no protection.
- A stub returns 42 and the test asserts 42. The code under test could be deleted and the test would pass.
- A failing assertion "fixed" by pasting the actual value into the expectation.
- An in-memory database standing in for the production engine. See `verify-before-done` for the differences.
- One huge end-to-end scenario that covers ten rules and fails for ten reasons.
- A transport-security header test that runs over plain HTTP, where the framework never sends the header.
- A database maintenance statement inside the test's wrapping transaction, where the engine refuses or ignores it.
- A wait or read with a timeout that returns at once because its input is closed, so the timeout never ran.
- A rate limit that survives between runs in a cache table and fails the suite only when it runs in full.

## Done when

- Every critical path touched by the change has an allowed-case and a refused-case test, and breaking the guard
  turns a test red.
- Each test asserts behaviour and fails for one reason.
- Each new test was seen red against broken code, and no assertion was removed or loosened to get green.
- End-to-end suites run on their own database and ports and give the same result twice in a row.
- No test sleeps, reads the real clock or uses unseeded randomness.
- Intermittent tests are fixed, or quarantined with an owner and a date.
- The coverage gate names critical modules and changed lines, and any global number is informational.
- Boundaries with fakes have contract tests, and the browser journeys are few and named.
- For spike-prone services a spike test question and its limits are written down.

## References

- [references/risk-and-coverage.md](references/risk-and-coverage.md): read when you build the risk map, pick
  levels for the tests, or set a coverage gate.
- [references/flaky-and-determinism.md](references/flaky-and-determinism.md): read when a test fails
  intermittently or when you write tests that touch time, randomness, queues or shared state.
- [references/load-and-spike.md](references/load-and-spike.md): read when you plan a load, stress or spike test.

## Sources

- https://testing.googleblog.com/2020/08/code-coverage-best-practices.html: coverage is lossy, no ideal number,
  critical gaps matter more than the percentage, mutation testing for assertion quality, verified 2026-11-01.
- https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html: flakiness rates and the cost of
  ignored red builds, verified 2026-11-01.
- https://martinfowler.com/articles/practical-test-pyramid.html: pyramid, behaviour over implementation,
  contract tests, test duplication, verified 2026-11-01.
- https://martinfowler.com/articles/nonDeterminism.html: quarantine, sleeps, clocks, isolation, verified 2026-11-01.
- https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications: the trophy and its scope, verified
  2026-11-01.
- https://hypothesis.readthedocs.io/en/latest/ and https://stryker-mutator.io/docs/: property-based and mutation
  testing definitions, verified 2026-11-01.
- https://newsletter.kentbeck.com/p/canon-tdd: failing test before the change; tests without assertions,
  deleted assertions and pasted actual values named as mistakes, verified 2026-11-03.
- https://abseil.io/resources/swe-book/html/ch13.html: state testing over interaction testing, and why,
  verified 2026-11-03.
- https://jestjs.io/docs/snapshot-testing: focused, short snapshots reviewed as code, verified 2026-11-03.
- https://grafana.com/docs/k6/latest/testing-guides/test-types/: load test types and what each one answers,
  verified 2026-11-01.
