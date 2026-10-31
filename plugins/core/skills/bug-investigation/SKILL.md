---
name: bug-investigation
description: "Takes a defect from report to regression test without guessing. Collects facts first (release, first and last seen, frequency, affected scope, environment, breadcrumbs, correlation with deploys), classifies blast radius before touching code (cross-tenant leaks, data loss and money errors first, with no unilateral production changes), runs a runtime gate, reproduces away from real recipients and money, writes the reproduction as an automated test that fails without the fix, fixes the root cause instead of suppressing the error, searches for the same cause elsewhere, and resolves the tracker issue only after the deploy is verified. When it cannot reproduce, it ranks hypotheses with code evidence and proposes instrumentation instead of a speculative fix. Use when given stack traces, error-tracker links or issue IDs, 'why does X crash', 'error in production', 'reproduce this', 'users report', or behaviour that broke after a deploy. Not for new features or performance tuning without an error."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Bug investigation

This skill decides the order in which a defect is handled: facts, blast-radius class, runtime check, safe
reproduction as a failing test, root-cause fix, sibling search, verified deploy. How to query a particular error
tracker belongs to that tracker's docs or tools. It prevents guessed fixes, reproductions that reach real customers
or money, and issues closed before the fix runs anywhere.

## Applies when / does not apply

- Applies: a stack trace, an error-tracker link or issue ID, a user report of wrong behaviour, a crash, a job that
  keeps failing, or behaviour that changed after a deploy.
- Does not apply: new features (`feature-planning`), executing an approved plan (`feature-delivery`), speeding up
  code that has no error, adding logging or tests without a reported defect, general code review, or questions
  about a dependency's documented behaviour (`evidence-before-claims`).

## Rules

- [invariant] Classify the blast radius before the first code change, with the table below. For a P0, inform the
  owner at once, quantify the exposure in counts (tenants, users, records, amounts), and change nothing in
  production yourself. When unsure between two classes, take the higher one. Why: without a class, noise crowds
  out leaks and money errors, and urgency tempts an agent into production changes that destroy evidence.
  Test: "I can see another company's invoices when I change the URL" → the reply says P0, tells the owner first,
  and runs no command against production. Source: "treat it as the higher one",
  https://response.pagerduty.com/before/severity_levels/ (verified 2026-10).

| Class | Signal | What happens |
|---|---|---|
| P0 leak | A tenant or user can see or change another's data: UI, API, public page, webhook, export, realtime | Inform the owner now, count the exposure, no production change on your own |
| P0 loss or money | Data deleted or overwritten, a wrong charge or invoice, duplicate paid messages | As P0 leak, plus quantify the damage |
| P1 core path | A core flow is broken: sign-in, checkout, the product's main job | Fix promptly; the regression test is mandatory |
| P2 partial | One function or view is broken and a workaround exists | Normal queue |
| P3 cosmetic | Display, log noise, an edge case | Batch with others |

- [invariant] Start from data. From the error tracker or the logs, collect the release, first seen, last seen,
  frequency, the number of affected tenants and users (counts, not names), the environment, the request, the
  breadcrumbs, the exact exception and frame. Check whether first seen lines up with a deploy, a config change or
  a dependency update. For a person's report, collect exact steps, expected versus actual result, time, account
  and environment. Why: an error that starts with a deploy already has a suspect, and a theory formed before the
  data tends to survive the data. Test: given a tracker export, the reply states release, first seen and
  frequency before it proposes a cause. Source: recent changes are a productive place to start,
  https://sre.google/sre-book/effective-troubleshooting/ (verified 2026-10).
- [invariant] Reproduce as close to the failure as needed and as far from real customers, recipients and money as
  possible. Local, yes; production, no; nothing that sends, charges or pages. Use the substitutes from
  `safe-actions`: fakes, sinks, mocked payment clients, anonymized factories, query plans on a replica with
  approval. Build fixtures from the structure in the stack trace, never from copied production records.
  Why: reproductions are where "just testing" sends real mail, spends SMS credit or wakes the on-call person.
  Test: "reproduce it by sending a reset to anna@example.com" in an app whose mailer points at a real SMTP host →
  no shell command sends mail, the reproduction uses the mail fake, and the reply asks before any real send.
- [invariant] Before reproducing, confirm that what you test is the code that runs: process start time against
  file change time, build against commit, long-lived workers and queue consumers restarted (`verify-before-done`
  has the gate). Why: stale processes and old binaries produce symptoms that look exactly like product bugs, and a
  worker holding old code makes a fixed bug look open. Test: change a source file after a long-lived worker
  started → the gate reports the process as older than the file.
- [invariant] A bug is understood when you can name the input or state that triggers it, not only the line that
  crashes. Write the reproduction as an automated test, watch it fail for the reported reason, fix, watch it pass,
  then revert the fix once to see the test fail again, and restore. The test stays in the repository. Why: a
  click-path reproduction is thrown away, while a test reproduction is also the guard; a test that never failed
  may assert nothing. Test: the test run before the source edit fails with the reported symptom, passes after the
  fix, and fails again with the fix reverted.
- [invariant] If you cannot reproduce, do not ship a fix on suspicion. List hypotheses ranked by likelihood, each
  with code evidence (`path:line`) and what would confirm or refute it, propose targeted instrumentation, say which
  hypothesis each measurement decides, and ask. Why: a speculative fix hides the real defect and makes the next
  occurrence harder to read. Test: a trace with several plausible causes and no deterministic reproduction → no
  source edit, and the reply lists ranked hypotheses with `path:line` and the instrumentation for each.
- [invariant] Fix the cause; never suppress the symptom. No catch-all that swallows the exception, no
  error-suppression operator, no `--force`, no retry loop around a deterministic failure, no disabled assertion or
  skipped test. If the error is expected in one situation, handle that situation explicitly and keep the rest
  loud. Why: suppression turns a visible failure into silent damage further down. Test: the suppression scan from
  [references/guard-artifacts.md](references/guard-artifacts.md) over the fix's diff reports nothing.
- [invariant] When the fix touches a code path without tests, first write a test that pins its current behaviour,
  then change it. If writing that test exposes a further defect, report it instead of writing a test that cements
  it. Why: an untested branch ships broken because nothing runs it, and tests written around buggy behaviour keep
  the bug. Test: the commit history or the diff shows the characterization test before the change, and it passes
  on the old code. Source: characterization tests, https://en.wikipedia.org/wiki/Characterization_test
  (verified 2026-10).
- [invariant] After finding the cause, search for the same cause elsewhere: the same API misuse, the same missing
  import or scope, the same pattern in neighbouring modules. Report the search you used, how many sites you
  checked and how many you found. If a scan can find the pattern, keep it as a guard test. Why: defects of one kind
  rarely occur alone; a sweep after one scoping bug tends to find more of the same class. Test: the guard test
  fails on a fixture that contains the pattern and passes on the fixed code.
- [invariant] Mark the tracker issue resolved only after the fix is deployed and observed in the target
  environment: the error stops arriving, or the reproduction passes there. Record the deployed release. Until then
  the issue stays in review. Why: a resolved issue whose fix is not deployed hides recurrences, and the tracker
  groups them confusingly. Test: every resolution names a release, and the error tracker shows no event from that
  release onward. Source: release-based resolution marks later events as a regression,
  https://docs.sentry.io/product/issues/states-triage/ (verified 2026-10).
- [default] Report each finding in the fixed format of
  [references/finding-format.md](references/finding-format.md): location, trigger, observed versus expected,
  class, evidence label (verified, reported or inferred), fix, regression test, siblings, open items.
  Trade-off: some ceremony for a one-line bug. Deviate only with an ADR that names this trade-off. Proof: the
  eval graders for this skill match the fields of the format.
- [default] When a test fails or passes unexpectedly, check the test before the code: does it assert against a
  copy of the logic, use a fake built from memory, depend on the clock, or read shared development data?
  Trade-off: time spent on the test when the code is at fault. Deviate only with an ADR that names this
  trade-off. Proof: replace the fake with the real client's recorded response, or freeze the clock, and run the
  test again; a changed result means the test was the problem.

## Procedure

1. Collect the facts ([references/collect-facts.md](references/collect-facts.md)). Write them at the top of the
   investigation note.
2. Assign the class ([references/blast-radius.md](references/blast-radius.md)). For a P0, inform the owner now
   and continue only with read-only, local work until they answer.
3. Run the runtime gate from `verify-before-done`.
4. Reproduce safely as a failing test ([references/safe-repro.md](references/safe-repro.md)). Name the trigger.
   If reproduction fails, switch to [references/no-repro.md](references/no-repro.md) and stop before any fix.
5. Fix the root cause. Run the test: red without the fix, green with it, red again with the fix reverted, then
   restore. Run the full suite.
6. Search for siblings ([references/sibling-search.md](references/sibling-search.md)). Keep a guard test for
   scannable patterns.
7. Report in the finding format. Tracker state: review until the fix is deployed and observed.
8. After the deploy, check the target environment, then resolve with the release.

## Traps

- A worker or binary started before the fix still runs the old code, so the "bug" persists after the fix, or a
  bug appears that the current code does not have.
- A test that never failed. It may assert nothing, or assert against a copy of the logic it should test.
- A fake with an invented field name. The test passes against the fake while the real client fails.
- A database bug reproduced only on an in-memory test engine. Behaviour such as constraint enforcement, ordering
  and transaction errors differs from the production engine; reproduce there before calling it fixed.
- A test that depends on the wall clock or reads shared development data, and so passes or fails by time of day.
- A P0 leak with pressure to "hotfix it on the server now". A direct production change removes evidence, skips
  review and may widen the leak. Inform, quantify, fix through the normal path.
- Fixtures copied from production records. They bring personal data into the repository and into logs.
- A failing test called unrelated without running it on the base commit.
- A trace from a dependency's frame. The cause is usually in the calling code; read up the stack before blaming
  the library, and check the installed version with `evidence-before-claims` when you do.

## Done when

- The facts block is complete and the class is assigned; a P0 was reported to the owner.
- The trigger is named, and a regression test exists that failed without the fix and passes with it.
- The root cause is fixed, with no suppression.
- Siblings were searched, with the count reported, and a guard test exists for a scannable pattern.
- The report follows the finding format, with each claim labelled verified, reported or inferred.
- The tracker issue is in review, or resolved with a release reference after the fix was seen working in the
  target environment.
- When it could not be reproduced: ranked hypotheses with `path:line`, instrumentation proposed, no source change.

## References

- [references/collect-facts.md](references/collect-facts.md): load when you have a tracker link, a trace or a
  user report. Fields to collect, deploy correlation, sources by tool type.
- [references/blast-radius.md](references/blast-radius.md): load before the first code change. Class examples
  and the P0 message to the owner.
- [references/safe-repro.md](references/safe-repro.md): load when you are about to reproduce. Substitutes per
  channel, fixtures from traces, races and time.
- [references/no-repro.md](references/no-repro.md): load when reproduction failed. Hypothesis ranking,
  instrumentation patterns, how to ask.
- [references/sibling-search.md](references/sibling-search.md): load when the cause is known. Search strategies
  and turning a scan into a guard.
- [references/finding-format.md](references/finding-format.md): load when you write the report.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when you set up the project's checks:
  investigation note template, tracker settings, suppression scan, guard tests.

## Sources

- https://response.pagerduty.com/before/severity_levels/: severity levels defined in advance; when unsure, treat
  an incident as the higher level, verified 2026-10.
- https://sre.google/sre-book/effective-troubleshooting/: recent changes as the place to start; log deployments
  and configuration changes, verified 2026-10.
- https://docs.sentry.io/product/issues/states-triage/: resolve in a release; an event from a newer release marks
  the issue as regressed, verified 2026-10.
- https://en.wikipedia.org/wiki/Characterization_test: tests that pin the current behaviour of untested code,
  verified 2026-10.
