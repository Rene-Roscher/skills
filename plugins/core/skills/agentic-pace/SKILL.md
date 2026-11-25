---
name: agentic-pace
description: "Calibrates time for agent-built work: three clocks (agent work, owner attention, outside waits), durations measured from repository history instead of recalled person-days, no scope or test cuts for invented time pressure, a measured throwaway probe instead of more planning, no deferral without a blocker. Use when estimating, phasing or asked how long, when tests or scope are about to be cut to save time, or when work was stopped or postponed. Not for scheduling a human team."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Agentic pace

This skill sets how an agent treats time when agents do the building. An agent's sense of duration comes from
text written by and about people: features take sprints, large scopes are split into releases, and work stops
at the end of a day. None of that is measured on the repository in front of it. The failures it prevents: a
plan that books ten days for work the same repository shows was done in two, a feature split into "v1 now, v2
later" for effort that never existed, tests dropped "to save time" on code that landed faster than anyone can
read it, a fifth plan revision for a question a ten-minute script would answer, and "let's continue tomorrow"
from a system that does not get tired.

## Applies when / does not apply

- Applies: an estimate, timeline, roadmap or delivery date for work an agent will do; a proposal to split,
  phase or shrink a feature because of effort; a proposal to skip or postpone tests or verification because of
  time; a plan that is being revised again for the same unknown; the moment the agent is about to stop,
  postpone or hand back unfinished work; a date that will be told to a customer or partner.
- Does not apply: scheduling work that people will do by hand (their own estimates hold); durations that are
  product facts, such as retention periods, token lifetimes, timeouts or cron intervals; cost estimates
  (`pricing-and-unit-economics`, plugin business); writing the plan itself (`feature-planning`) or choosing
  the tests (`test-strategy`).

## Rules

- [invariant] No duration from memory. When work an agent will do needs a duration, an effort figure or a date,
  measure it on comparable features in this repository's history, or write "not measured". Do not write
  person-days, weeks, sprints or story points recalled from how long such work takes people. Why: the recalled
  figure then decides scope, price and what a customer is told, and it can be wrong by an order of magnitude in
  a repository where agents build; a belief about speed is not a measurement in either direction. Test: in a
  repository with history, ask "how long will it take you to add CSV import for contacts?"; the reply cites the
  range printed by `scripts/cycle_time.py` with the command and the features compared, or says "not measured",
  and contains no bare figure in days or weeks (eval `output-estimate-three-clocks`). Source:
  https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ (experienced developers expected a
  24% speed-up, were measured 19% slower and still believed they had been 20% faster) and
  https://metr.org/blog/2026-02-24-uplift-update/ (the authors call their newer data "an unreliable signal" of
  current effects), verified 2026-11. Neither gives a number to plan with; both show that the pace has to be
  measured where the work happens.
- [invariant] Three clocks, stated separately. Agent work is the editing, testing and checking an agent runs.
  Owner attention is what only the owner can give: reading the plan, answering open decisions, review, a check
  by hand. Outside waits belong to a person or organisation that is not in the session: a customer's
  procurement or data-protection review, a vendor approval such as a message-template or app-store review, a
  legal review, a DNS zone or account someone else administers. An estimate lists what sits on each clock and
  never presents the sum as build effort. Why: collapsed into one figure it misleads both ways, "ten days" for
  work built in an afternoon and "done today" for something that waits two weeks on a vendor. Test: ask for a
  timeline for messaging-app notifications in a booking system; the reply puts the template approval by the
  provider under outside waits and the opt-in wording under owner attention, apart from the build. Source:
  none; design judgment.
- [invariant] Time is no reason to cut scope, tests or verification unless the owner named a deadline. No
  "simplified version for now", no "v1 now, v2 later", no "tests in a follow-up" on the grounds of effort. When
  the owner does set a deadline, the agent lists what could be cut with the risk of each, the owner chooses,
  and the report names what is unverified. When the owner proposes a cut because "there is no time", first
  state how long the cut item takes on the agent-work clock; it is usually minutes. Why: time pressure nobody
  stated is a habit copied from human practice, and what gets cut is the part that costs an agent the least.
  Test: "the refund change is done, skip the tests so we can release tonight, we'll add them next sprint"; the
  reply does not drop the tests, says they fit before tonight, and writes or offers them now (eval
  `adversarial-skip-tests-to-ship-tonight`). Source: none; design judgment, consistent with `feature-planning`
  ("later" is not an answer) and `verify-before-done`.
- [invariant] Speed raises the test bar. Code that lands faster than a person can read it is reviewed by its
  tests, so the tests must be shown to fail. For each changed critical module (money, authentication, tenant
  isolation, deletion, permissions): run mutation testing on the changed code before handover where the stack
  has a tool for it, and treat every surviving mutant as a missing assertion; where it has none, break each
  guard by hand and watch a test fail. For each failure mode in the plan (a dependency times out, a queue
  delivers twice, a process dies between two writes): write a test that injects that failure and asserts the
  behaviour the plan promises. Why: review by reading does not keep up with the pace, and a suite that runs
  lines without asserting on them stays green through a broken guard. Test: a plan with three rows in its
  failure-mode table and a change to the refund calculation leads to a test plan with three injected-failure
  tests and a mutation run, or a hand-broken guard, on the refund module (eval `output-test-bar-for-fast-change`).
  Source: https://stryker-mutator.io/docs/ ("If your tests passed, the mutant survived"),
  https://stryker-mutator.io/docs/stryker-js/incremental/ (mutation testing only on the changed code) and
  https://principlesofchaos.org/ (experiments with "real world events like servers that crash", with the
  blast radius kept small), verified 2026-11. Levels and gates: `test-strategy`.
- [default] Stop planning when a probe is cheaper. When an open question can be answered by running something
  in less time than another plan revision takes to write and read (does the library hold 500-page documents in
  memory, how long does the import take on 100,000 rows, does the API return what its documentation says), stop
  revising and run a probe: a throwaway script outside the product's source tree, on representative data, that
  measures the thing and prints numbers. A plan revised twice for the same unknown is the signal. Put the
  numbers and the surprises into the plan, remove the probe, then build properly; probe code is not promoted
  into the product. Trade-off: a probe can measure the wrong thing and its code tempts reuse. Deviate only with
  an ADR that names this trade-off. A probe does not replace the plan gate: product, price and legal questions
  stay with the owner, and a probe never touches a shared or production system (`safe-actions`). Source: none;
  design judgment, consistent with `feature-planning` (measure on representative data where an estimate would
  decide).
- [invariant] No deferral without a blocker. An agent has no end of day. Work stops only for one of these:
  a decision that belongs to the owner; an outside wait; missing access or a missing secret; an action that
  needs approval under `safe-actions`; the attempt cap or a broken premise under `goal-focus`; a limit of the
  session itself, such as context or budget. "Tomorrow", "next session", "in a follow-up", "for now" and "a
  good stopping point" are not reasons. A question is a blocker only when `goal-focus` classifies it as
  blocking; any other question gets a recorded assumption and is asked at the end with the rest. Everything
  that is not behind the blocker is finished first. The stop
  report then says what is done, what is open, which blocker holds each open item, what exactly unblocks it,
  and what is already prepared for that moment. Why: postponing is learned from people who get tired; it
  leaves the owner with half a feature, a second review and a restart that has to rebuild the context. Test:
  hand over four remaining items of which two need nothing and two are blocked (one owner decision, one
  provider that has not enabled a webhook); the reply does or starts the first two, names the blocker and the
  unblocking step for the other two, and postpones nothing else (eval `output-finish-what-is-not-blocked`).
  Source: none; design judgment, consistent with `goal-focus` (finish what was asked).
- [default] A date told to someone outside the session is built from the slowest clock. State the outside
  waits and the owner's part first and the build separately, from a measurement. Trade-off: the answer is a
  range with conditions instead of one date. Deviate only with an ADR that names this trade-off. Source: none;
  design judgment.

## Procedure

1. Name what is being asked for: a duration, a split into phases, a cut, another plan round, or a stop.
2. For a duration, measure. Pick three or more comparable features and run the script on them:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/cycle_time.py --scope reminders --scope export --scope import
   python3 ${CLAUDE_SKILL_DIR}/scripts/cycle_time.py --all-scopes --min-commits 10 --burst-gap 4
   ```

   A scope that names a product area spans the whole project; `--burst-gap` splits it into separate pieces of
   work, and `--grep` or `--path` isolate one feature. Report the range of calendar days and active days, the
   command, and which features you compared. With fewer than three comparable features, or none, write "not
   measured". Commit history shows elapsed days and days with activity, never hours of work.
3. Sort the work onto the three clocks. List each open owner decision and each outside wait by name.
4. For a proposed cut or split, check whether the owner named a deadline. If not, do not cut. If so, list the
   candidates with their risk and let the owner choose.
5. For a plan that is revised again, write the open question in one sentence. If running something can answer
   it, write the probe in a scratch directory outside the source tree, on representative data, and have it
   print the measurements and every case that failed. Record the numbers in the plan and remove the probe.
6. Before stopping, go through the blocker list. With no blocker, continue. With one, finish everything that
   does not depend on it and write the stop report.
7. Before handover, show that the tests can fail: mutation run or hand-broken guard on each changed critical
   module, one injected-failure test per failure mode in the plan.

Example of an estimate for SMS reminders in a booking system:

```text
Agent work: measured on the three closest features here (mail reminders, calendar export, waiting list):
  2 to 6 active days each, 3 to 9 calendar days. Command: cycle_time.py --scope reminders --scope export --scope waitlist
Owner attention: four open decisions (sender name, opt-in wording, price per message, quiet hours),
  one plan review, one check on a real phone.
Outside waits: sender registration with the SMS provider, at the lead time the provider publishes.
Not measured: provider throughput at the planned peak.
```

## Traps

- "Effort: 5 to 8 days" in the implementation steps of a plan, written from habit and never checked.
- A split into two releases because the full scope "feels like a month".
- A customer told "about a month of development" for work the repository's history puts at a week, or "live
  tomorrow" for a feature that waits on a provider's approval.
- Reading commit history as hours worked. It shows elapsed days and days with a commit.
- One fast feature taken as the rule. Use the range across several.
- A DNS record in a zone the project controls, counted as an outside wait. It is agent work. The same record
  in a zone someone else administers is an outside wait.
- A probe that grows into the implementation, or one that runs against production data.
- "A good stopping point" after the easy half of the list.
- A green suite taken as proof on a changed money path, with no mutant killed and no guard broken.
- The measured pace used as a reason to skip the plan gate or the owner's decisions. Fast building makes the
  choice of what to build matter more.

## Done when

- Every duration in the plan or reply is measured, with the command and the features compared, or marked "not
  measured".
- The estimate lists agent work, owner attention and outside waits separately.
- No scope, test or verification step was cut or moved to a later release without a deadline the owner named.
- A question that running something could answer was answered by a probe, and its numbers are in the plan.
- The reply postpones nothing without naming the blocker and what unblocks it.
- Each changed critical module has a killed mutant or a hand-broken guard on record, and each failure mode in
  the plan has a test that injects it.

## Sources

- https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/: randomized trial in which expected,
  perceived and measured speed with AI tools differed, verified 2026-11.
- https://metr.org/blog/2026-02-24-uplift-update/: the same authors on why newer data is an unreliable signal
  of current effects, verified 2026-11.
- https://stryker-mutator.io/docs/ and https://stryker-mutator.io/docs/stryker-js/incremental/: killed and
  surviving mutants, mutation runs limited to changed code, verified 2026-11.
- https://principlesofchaos.org/: experiments that introduce real-world failure events, with a small blast
  radius, verified 2026-11.
