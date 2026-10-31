---
name: verify-before-done
description: "Separates tested from verified, and merged from live, before reporting done: a runtime gate on the running code, regression tests that fail without the fix, test-versus-production gaps, no vacuous checks. Use when about to say done, fixed, works, shipped or live, when a fix has no effect, before closing a ticket, or when writing regression tests or CI gates. Not for planning or triage."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Verify before done

This skill decides what may be called done. Done means the behaviour was seen working in a running system;
green tests are a weaker status, and the report says which one applies, item by item. Test frameworks and CI
syntax stay with their vendors' docs. The failure it prevents: an item reported as done that does not work,
because the tests ran against something other than what production runs.

## Applies when / does not apply

- Applies: you are about to say done, fixed, works, ready, shipped or live; tests pass but the behaviour is in
  doubt; a fix seems to have no effect; a ticket is about to be closed; you write a regression test, a guard
  or a CI gate.
- Does not apply: planning (`feature-planning`), code style, or first-pass bug triage
  (`bug-investigation`). Facts about libraries and APIs belong to `evidence-before-claims`.

## Rules

- [invariant] Report every item with exactly one status: implemented (code written), tested (automated tests
  pass), verified (you watched the behaviour in a running system: the real UI, endpoint, job, CLI or device),
  deployed (the release run succeeded), live (seen at the production surface). Done requires verified; a
  release task requires live. Otherwise write "tested, not verified" with the reason, and move the tracker
  item to its review or needs-verification state, never to done. Why: green CI proves something was built,
  not that it does what was asked; items were closed that changed nothing on screen, or covered one call site
  out of many. Test: ask the agent to mark a task done when the app cannot start in the run; the reply says
  tested, not verified, and names why (eval `output-green-not-verified`).
- [invariant] Before you debug local behaviour or claim it works, prove that the code you read is the code
  that runs: process or container start time against the change time of the files, build time against the
  last commit that touched the source, which process owns the port and where it was started from. Long-lived
  processes keep old code: queue workers, persistent app servers, stream consumers, schedulers, dev servers
  that compile config at boot. Restart the ones you started; ask before you touch anyone else's, as
  `safe-actions` describes. Why: an outdated, hand-started binary reproduced an already-fixed limit and looked
  like a product bug for hours; queue workers running since the day before failed every job on a newly added
  enum case. Test: a built file older than its source answers with the old value; the agent compares
  timestamps and rebuilds instead of editing the source (eval `adversarial-stale-build`).
- [invariant] Prove each regression test can fail: revert or mutate the fix, run the test and see it red,
  restore the fix and see it green, and report both runs. Guards, scanners and CI gates get the same
  treatment: show one input they reject. Why: a test that never failed is not evidence; tests were green while
  asserting nothing, and scanners reported zero findings because they matched nothing. Test: the agent runs
  the test at least twice and reports the red run (eval `output-prove-test-fails`).
- [invariant] Tests read what the system produced: the HTTP response, the rendered page data, the rendered
  mail, the stored row. Never rebuild the expression under test inside the test and assert against the copy.
  Why: a test rebuilt the expression that decides whether a feature is shown, with its own default, and stayed
  green while the real code hid the feature from every user. Test: change the default in the production code;
  the test goes red. If it stays green, it asserts a copy.
- [invariant] Run the required test suite on the production database engine and the production runtime minor.
  Keep the target runtime version in one place and make the test bootstrap abort on a mismatch. An in-memory
  database lane is fine for fast feedback; the required check runs on the production engine. Why: PHP 8.4
  changed `round()` results for some float edge cases, and a first suite run on PostgreSQL exposed failures
  that were green on an in-memory engine, among them a missing `ORDER BY` and a caught unique violation that
  aborts the whole PostgreSQL transaction. Test: insert a duplicate inside a transaction, catch the error,
  run one more statement; it passes on SQLite and fails on PostgreSQL with "current transaction is aborted".
  Source: https://www.postgresql.org/docs/current/tutorial-transactions.html,
  https://www.postgresql.org/docs/current/queries-order.html,
  https://github.com/php/php-src/blob/PHP-8.4/UPGRADING (verified 2026-10).
- [invariant] For the change at hand, name how the test environment differs from production and check those
  paths outside the default suite: sync instead of async queues, fakes that never render, configuration or
  components that exist only in tests, pending schema changes, several writes in the same second, shared dev
  stores, mock endpoints in the dev stack. Why: each of these let a green suite ship a production or dev
  incident. Test: the completion report lists the differences that applied and how each was checked; a guard
  that reads data written by a queued job is tested with the queue faked, so the async write is absent.
- [invariant] No vacuous green. A filtered test run asserts a minimum test count, a scanner fails when its
  fixture yields nothing, an artifact upload fails when no file matches, a missing tool fails the job instead
  of skipping it, and `|| true` or `continue-on-error` carries a written reason. The local "run CI" command
  runs the same job list as CI. Why: some runners exit 0 when a filter matches nothing, so renaming a test
  leaves a required job green and empty. Test: `go test -run NoSuchTest ./...` prints `[no tests to run]` and
  exits 0 (go1.27.3, run 2026-10-31); rename the guarded test and the required job must go red. Source:
  https://github.com/actions/upload-artifact (`if-no-files-found` defaults to `warn`, verified 2026-10).
- [invariant] Merged is not deployed, and deployed is not live. Before you say live, confirm the deploy run
  ran and succeeded, then observe the change at the production surface: a version endpoint or header, the
  changed response, the rendered page. If you cannot reach production, write "merged, deploy not confirmed".
  Why: hosted CI runners stopped starting jobs after a billing failure, and merged documentation was never
  deployed while everyone assumed it was. Test: a post-deploy check compares the version the app reports with
  the version the release run wrote, and fails on a mismatch.
- [invariant] Apply schema changes to the real dev database and confirm none are pending before any
  end-to-end claim. In rollout plans the schema change ships before the code that needs it (expand, then
  contract). Why: a large suite was green, and the first real run of a scheduled job died on a missing column
  because the migration was never applied. Test: the local end-to-end entry point and the deploy pipeline fail
  when the framework's migration status lists a pending migration.
- [invariant] Track each requested item separately, verify each one, and report each with its status. Never
  write "all done" while one item is only tested or not started. Why: parts of multi-point requests were left
  unfinished while the summary said done. Test: a three-item request where one item cannot be verified in the
  run; the report gives three statuses and does not call the request done (eval `output-multi-item-status`).
- [invariant] Name every failing test, command or check with the relevant output lines. "Some unrelated tests
  fail" needs the list and the evidence that they are unrelated. Why: glossed-over failures hide regressions
  and make every later report less trustworthy. Test: with one failing test in the suite, the report contains
  that test's name and its assertion message.
- [default] Run package managers, builds and tests with the versions CI and production use, through the CI
  image or a container, and verify lockfile changes with a clean install in that image. Trade-off: a slower
  local loop. Deviate only with an ADR that names this trade-off and pins the host tool versions. Test: a
  lockfile written by a host package manager one minor off fails the clean install in the CI image.
- [default] Visual claims are measured, never eyeballed: element screenshots, overflow checks that include
  clipping parents, computed contrast, sizes at real viewports, run headless. The method belongs to
  `browser-verification`; this rule only rules out "looks fine" as evidence. Trade-off: measuring takes longer
  than looking. Deviate only with an ADR that names this trade-off. Test: a self-check that skips containers
  with hidden overflow reports clean on a layout whose columns overflow; the measured check fails it.
- [default] Scripts that prove behaviour (inspectors, range-request tests, layout checks) live in a tracked
  `scripts/` or `tools/` folder, not a temporary directory. Trade-off: more files in the repository. Deviate
  only with an ADR that names this trade-off; a one-off script whose output is attached to the report needs
  none. Test: after a reboot, the regression can still be re-checked from the repository alone.

## Procedure

1. Write down the user's items verbatim. Each one gets its own status at the end.
2. Gate: run the runtime gate. Read [references/runtime-gate.md](references/runtime-gate.md) for the commands.
   Restart only what you started.
3. Run the tests on the production engine and runtime. For each regression test, do the red-green run.
4. Name the test-environment differences that apply and check each one. Read
   [references/test-env-lies.md](references/test-env-lies.md) when the change touches queues, mail, config,
   schema, time or shared stores.
5. Observe the behaviour in a running system: the UI, the endpoint, the job, the CLI. For UI, measure it.
6. For a release task, confirm the deploy and observe the change in production. Read
   [references/deploy-verification.md](references/deploy-verification.md). Actions that leave the machine
   follow `safe-actions`.
7. Report per item with the status ladder and the evidence. Read
   [references/completion-report.md](references/completion-report.md) for the template.

## Traps

- A filtered test run that matched nothing and exited 0.
- A queue worker or app server that loaded the code before your change.
- A mail fake that never renders the template, so broken links and escaping go unseen.
- A component booted in tests but not in queue workers, so the job fails only in production.
- A migration written but not applied. The in-memory suite builds the schema from migration files and never
  notices.
- A dev-stack mock endpoint that answers with canned data instead of the real service.
- A green pipeline whose deploy job never started.
- A host package manager that rewrote the lockfile, so CI's clean install fails.

## Done when

- Every requested item has one status from the ladder and the evidence behind it.
- Done is used only for verified items, and for release tasks only for live ones.
- Each regression test was seen red without the fix and green with it.
- The applicable test-environment differences are named with how each was checked.
- Failing checks are listed with their output.
- Items that are not verified sit in the tracker's review or needs-verification state.

## References

- [references/runtime-gate.md](references/runtime-gate.md): read when local behaviour does not match the code,
  or before any end-to-end claim.
- [references/test-env-lies.md](references/test-env-lies.md): read when tests are green but you doubt
  production behaviour, or when you write a guard.
- [references/vacuous-green.md](references/vacuous-green.md): read when you write or review CI gates, scanners
  or filtered test runs.
- [references/completion-report.md](references/completion-report.md): read when you are about to report
  completion.
- [references/deploy-verification.md](references/deploy-verification.md): read when the task ends in "live".
- [references/guard-artifacts.md](references/guard-artifacts.md): read when the project should enforce these
  rules in its own repository.

## Sources

- https://www.postgresql.org/docs/current/tutorial-transactions.html: an error puts the transaction block in
  aborted state, and only `ROLLBACK TO` or a full rollback regains control (PostgreSQL 18), verified 2026-10.
- https://www.postgresql.org/docs/current/queries-order.html: without `ORDER BY`, row order is unspecified and
  must not be relied on, verified 2026-10.
- https://github.com/php/php-src/blob/PHP-8.4/UPGRADING: `round()` results changed for some float edge cases,
  verified 2026-10.
- https://github.com/actions/upload-artifact: `if-no-files-found` accepts `warn`, `error` and `ignore`, default
  `warn` (README for v7), verified 2026-10.
- https://docs.pytest.org/en/stable/reference/exit-codes.html: pytest exits with code 5 when no tests were
  collected, verified 2026-10.
- https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md: fresh
  verification evidence before any completion claim; this skill adds the runtime gate, test-environment
  differences and the deploy ladder, verified 2026-10.
