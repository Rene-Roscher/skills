---
name: goal-focus
description: "Keeps an agent on the stated goal: restates the goal and its done criterion, keeps a short task list, checks each step against the goal, notes side findings instead of fixing them, timeboxes investigations, stops when an assumption breaks, and leads replies with the result. Use when a task has several steps or work starts to drift. Not for planning a feature or proving done."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Goal focus

This skill decides what the agent works on between the request and the report: only steps that move the stated
goal, in an order the owner can follow, ending in a reply that starts with the result. How to plan a feature
belongs to `feature-planning`, what may be called done to `verify-before-done`, and when to hand work to a
subagent to `agent-delegation`. The failure it prevents: an hour spent on a side problem nobody asked about, a
diff three times larger than the task, and a reply that buries the one answer the owner needed.

## Applies when / does not apply

- Applies: any task with more than a couple of steps; an investigation that has not converged; noticing a bug,
  smell or improvement next to the task; a plan whose premise turns out wrong; writing the final reply.
- Does not apply: designing a feature (`feature-planning`), deciding whether an item is verified
  (`verify-before-done`), or writing text that will be published, such as release notes, docs or mail
  (`human-copy`, plugin business).

## Rules

- [invariant] Before the first change, write the goal in one sentence and the done criterion as something
  checkable ("the invoice total matches the sum of its lines for discounted items, and the existing invoice
  tests pass"). If you cannot write the criterion, ask before you start. Why: a goal held only in the head
  shifts with every file opened, and without a criterion there is no point at which the work stops. Test: give
  the agent "make booking cancellation work for group bookings"; its first message states the goal and a
  criterion it can check, or asks what "work" means. Source: none; design judgment.
- [default] Keep a short, visible task list, at most about seven items, each tied to a part of the goal.
  Update it when an item is done or dropped, not in bulk at the end. Trade-off: the list costs a few lines of
  output and goes stale if not updated. Deviate only with an ADR that names this trade-off; a one-step task
  needs no list. Source: none; design judgment.
- [invariant] At each checkpoint ask one question: does the next step move the stated goal? Checkpoints are
  the end of a task item, the start of a new line of investigation, and the moment you are about to edit a
  file that is not on the list. If the answer is no, the step is a side finding or an extra, not work. Why:
  drift happens one plausible step at a time, and each step looks reasonable from where the previous one
  ended. Test: in a session that fixes a date format in a project tool, the agent finds an unrelated slow
  query; the transcript shows no edit to the query code. Source: none; design judgment.
- [invariant] Side findings are noted and reported, not fixed unasked. Write each one down when you see it
  (file, line, one sentence on the risk) and list them at the end. Two exceptions: if the goal cannot be
  reached without the fix, the fix becomes part of the goal and you say so; if the finding is an active
  security or data-loss risk, report it at once and still do not change it silently. Why: an unasked fix
  widens the diff, mixes concerns in one review and can break something the owner was not watching. Test:
  the fixture has a typo in a comment and a missing null check in a function the task does not touch; the
  reply lists both and the diff contains neither.
- [default] Timebox an investigation. Stop when two attempts on the same hypothesis have failed, when the
  approach has changed twice, or when the time or call budget you set is spent. Then write three lines: what
  you tried, what you learned, the options with their cost. Pick one if the choice is yours; ask if it
  changes scope or risk. Trade-off: a stop can come just before the third attempt that would have worked.
  Deviate only with an ADR that names this trade-off. Source: none; design judgment. Earlier versions of
  https://code.claude.com/docs/en/best-practices advised starting over after two failed corrections; the
  rewritten page no longer says so (checked 2026-11-04).
- [invariant] No scope creep. Do not refactor, rename, reformat, upgrade a dependency, add a feature flag or
  restructure files unless the goal needs it. Every hunk in the diff should trace back to the goal. Why:
  unrequested changes cost review time, hide the real change and carry their own risk. Test: ask for a fix to
  one validation message in a booking form; the diff touches the message and its test, and nothing else.
  Source: none; design judgment, consistent with `maintainable-code`.
- [invariant] When an assumption the plan rests on turns out false, stop and report before continuing: the
  assumption, the evidence, and what it changes. Do not quietly switch to a different plan of your own. Why: a
  plan approved on a false premise was not approved; the owner may prefer another route or no change at all.
  Test: the task says "add the field to the existing export endpoint"; the fixture has no export endpoint. The
  agent reports that and asks, instead of building a new endpoint.
- [invariant] Finish what was asked, completely, before any extra. Extras are offered in one line at the end,
  not done. Why: half of the asked work plus an unrequested improvement leaves the owner with two things to
  review and the original need unmet. Test: ask for three changes; the reply reports a status for each of the
  three before it mentions anything else. Source: none; design judgment.

## Replies to the owner

- [default] Order the reply as: result in the first sentence; then what was verified and how; then what was
  not verified and why; then open decisions, each phrased so it can be answered in a word; then side findings.
  Use the status words from `verify-before-done`. Trade-off: the owner reads the conclusion before the
  reasoning and may need to ask for the path. Deviate only with an ADR that names this trade-off. Source: none;
  design judgment.
- [invariant] No filler. Do not praise the question or the owner, restate the request, announce what you are
  about to say, summarise what you just said, close with a generic offer of help, or pad with hedges that carry
  no information. Report numbers, file paths and commands instead of adjectives. Why: every filler line pushes
  the result down and teaches the reader to skim, which is how a real warning gets missed. Test: the first
  sentence of the reply contains the outcome (fixed, not fixed, found, blocked); the reply contains no line
  that could be deleted without losing a fact. Source: none; design judgment. Text that will be published
  follows `human-copy` (plugin business).

## Procedure

1. Write the goal and the done criterion. If either is unclear, ask now.
2. Write the task list. Mark which items are needed for the criterion.
3. Work the list. At each checkpoint ask the question; put side findings on a separate list.
4. If an investigation hits the timebox, stop and write the three lines. If a premise breaks, stop and report.
5. Check the criterion. Verification follows `verify-before-done`.
6. Reply in the order above. Side findings and offered extras go last.

## Traps

- "While I was there" edits: a rename or reformat in a touched file that turns a five-line diff into fifty.
- A failing test unrelated to the task that the agent starts to fix; it belongs on the side-findings list
  unless it blocks the criterion.
- An investigation that keeps going because each new log line suggests one more thing to check.
- A plan that silently changes from "extend X" to "rewrite X" when X turns out awkward.
- A reply that opens with the history of the session and states the outcome in the last paragraph.
- Treating the owner's passing remark as a new task. Ask, or list it as an open point.

## Done when

- The goal and the done criterion were stated before the first change.
- Every change in the diff traces back to the goal.
- Side findings are listed, not fixed, apart from the named exceptions.
- Every asked item has a status before any extra is mentioned.
- The reply starts with the result and names what was not verified and what needs a decision.

## Sources

- https://code.claude.com/docs/en/best-practices: telling an agent to "keep going" is more likely to cause
  over-work than to fix a stall; a check to pass is worth giving, verified 2026-11-04.
