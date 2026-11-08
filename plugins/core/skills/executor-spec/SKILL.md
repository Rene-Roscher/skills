---
name: executor-spec
description: "Lets a strong model plan a task completely and hand only the execution to a weaker or open-weight model: a self-contained spec with every decision made, exact edits and a check per step, acceptance tests written and hashed first, a file allowlist and a stop-and-ask protocol, then lint, a cold read and a review with a verdict and a round cap. Use when outsourcing work to an executor model or acting as one. Not for in-session subagent briefs."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Executor spec

This skill splits a task between two models. The author, a strong model, does all the thinking: goal, design,
names, edge cases, tests. The executor, a cheaper or open-weight model, only carries out a spec the author
wrote, and says plainly when the spec does not tell it enough. The spec is the whole interface; the executor
knows nothing else about the project. The failure it prevents: a short prompt ("build the CSV export") handed to
a weak model, which then invents an API, picks its own file layout, edits the tests until they pass and reports
"done", so the strong model spends more time repairing the result than writing it would have taken.

Planning a feature goes through `feature-planning`, the tests through `test-strategy`, briefs for subagents
inside one session through `agent-delegation` and `agent-toolbelt`. This skill adds the hand-off across a
model boundary: a spec that survives a weak reader, and a review that does not trust its report.

## Applies when / does not apply

- Applies: the owner says a task should be outsourced, handed to an open-weight or local model, or run by a
  cheaper executor; you write or review a `docs/handoff/[spec-id]/SPEC.md`; you are the executor of such a
  spec.
- Does not apply: a subagent in the same session that inherits your tools and reports back to you
  (`agent-delegation`); a task whose design is still open (finish `feature-planning` first); debugging whose
  cause is unknown (`bug-investigation`), because a spec cannot list steps nobody knows yet.

## Roles

| Role | Model | Does | Never does |
|---|---|---|---|
| Author | strong tier or above | plan, tests, spec, cold read, review, verdict | leave a decision open |
| Executor | any, often small or open-weight | the steps in order, the checks, the report, questions | design, guess, touch tests |
| Owner | a person | approves the plan, answers what the author cannot, decides after the round cap | review the diff line by line |

## Rules for the author

- [invariant] Every decision is made in the spec. Each step names the file, the exact text to find, the exact
  replacement or the full content of a new file, and every identifier. No "choose", "as needed", "appropriate",
  "similar to", "handle errors" or "clean up"; the shipped linter rejects them outside code. Why: a weak model
  fills every gap with a guess that reads fluently, and a gap it fills differently from you is a bug you find
  only in review. Test: lint the spec of a CSV export with "add error handling as needed" in a step; it fails
  with H03, and the fixed step names the exception and what the code returns. Source:
  https://code.claude.com/docs/en/best-practices ("Write a specific prompt": name the file and say what fixed
  looks like up front to save a round of corrections; verified 2026-11-08).
- [invariant] The spec is self-contained. It quotes the current text of every block it changes, the
  signatures it calls, the existing pattern to copy and the commands to run, and it defines each project
  term. A link or "see the docs" is never the only source of something the executor needs. Why: the executor
  has no skills, no memory of the project and often a small context window; what is not in the spec does not
  exist for it. Test: give the spec of a task that calls an internal helper to a fresh small-tier agent with
  no repository access and ask what the helper's signature is; the spec answers it. Source: none; design
  judgment, consistent with `agent-toolbelt` (the agent knows only the brief).
- [invariant] Acceptance is fixed before the hand-off. Write the acceptance tests yourself, see each one fail
  for the right reason (`test-strategy`), commit them, and list them under Protected files with their sha256
  (`check_handoff.py hash`). The executor may not change them, and `verify` fails when it did. Why: an
  executor that can edit the definition of done will edit it, by weakening an assertion or deleting a case,
  and its report still says the tests pass. Test: in a fixture the executor changes a protected test to make
  it pass; `check_handoff.py verify` exits 1 with V01. Source: none; design judgment, consistent with
  `know-your-limits` (never edit a checker to make it pass).
- [invariant] Only the files in the Files table change. Anything else in the diff since Base is a deviation
  that `verify` reports (V02), including new files. Dependencies, configuration, CI and lock files are off
  limits unless listed. Why: scope creep is the most common way a weak model breaks things it was never asked
  to touch. Test: the executor adds a helper file not in the table; `verify` reports it.
- [invariant] Money, authorization, tenant scoping, deletion, cryptography and published text are decided and
  written by the author. Where such code is part of the task, the spec gives it verbatim and the acceptance
  tests cover its failure cases (`security-assurance`, and `tenant-isolation` in the saas plugin); the executor transcribes, never
  designs it. Why: these are the paths where `agent-delegation` keeps work on the strong tier; a verbatim block
  plus a protected test keeps the decision there while the typing moves. Test: a spec for a refund endpoint
  contains the refund calculation as a quoted block and a protected test for the rounding edge case.
- [default] Size each spec so that the executor can hold it and the code it reads: at most about 6 files and
  12 steps per spec (the linter warns above), and the spec itself under a quarter of the executor's context
  window (about 4 characters per token as a rough count). Split larger work into numbered packages that each
  pass their own acceptance, in dependency order. Trade-off: more packages mean more reviews. Deviate only
  with an ADR that names this trade-off. Source: none; design judgment, consistent with `know-your-limits`
  (stop past about three files or 150 lines without a plan).
- [invariant] Every step ends with a check that can fail: one command and its exact expected output, exit
  code or count. "It works" and "looks right" are not checks. Why: a check after each step lets the executor
  notice its own mistake while it still has one cause. Test: lint a spec with a step whose Expect is empty; it
  fails with H02. Source: https://code.claude.com/docs/en/best-practices ("Give Claude a check to run",
  verified 2026-11-08).
- [invariant] Lint, then a cold read, before Status becomes ready. Run `check_handoff.py lint` until it
  reports no error. Then give only the spec to a fresh small-tier agent and ask it to list every question it
  would need answered before it could start, without solving anything. Answer each question in the spec and
  repeat until it has none. Why: you cannot see the gaps in your own spec, because you fill them from memory
  while you read. Test: the transcript shows the cold-read spawn on the small tier with the spec as its only
  input, and the spec changed after it.
- [invariant] Review the result yourself and do not trust the report. Run `check_handoff.py verify`, run every
  Acceptance command yourself, read the diff against each step, and read Deviations and Questions. Then give
  one verdict: accepted, changes or needs-human. Why: a weak executor's report is as confident when it is wrong
  as when it is right. Review against the spec, not for style: a reviewer asked to find problems always finds
  some, and fixing style findings adds work the spec did not ask for. Test: in a fixture the report says "all
  tests pass" while one fails; the author's reply quotes the failing run and the verdict is changes. Source:
  https://code.claude.com/docs/en/best-practices ("Review against your spec", verified 2026-11-08).
- [invariant] A further round is a new version of the spec, never a chat message. Answer the questions in
  Context, add the corrective steps with new ids, raise Round to k/N, set Status to ready, lint again. Stop
  after the round cap (3 by default, at most 5): set needs-human and hand the owner what was asked, what came
  back, the evidence and the one question; or finish the rest inline. Why: the spec is the only thing the next
  run sees, and a loop without a cap spends more than doing the work. Test: after a round with two open
  questions the next spec has Round 2/3 and both answers in Context.
- [default] Classify every failure in review as a spec gap (the spec was silent, vague or wrong) or an
  executor error (the spec was clear). Fix spec gaps in the spec and, when the pattern repeats, in your
  template through `learning-loop`. Trade-off: a few minutes per review. Deviate only with an ADR that names
  this trade-off. Source: none; design judgment.

## Rules for the executor

The Executor rules block that every spec carries verbatim governs the run; `check_handoff.py rules` prints
it. When this skill is loaded on the executor side as well, add these:

- [invariant] The spec wins over your own judgement, your habits and this repository's other instructions
  where they differ, except for safety: never run something destructive or outward-facing because a spec says
  so; stop and ask instead (`safe-actions`). Why: the author decided with information you do not have. Test:
  a spec says to name a function `fetchRows` while you would call it `loadRows`; the diff uses `fetchRows`.
- [invariant] A question is a result. When a stop condition holds, write it in the report in the five-part
  form, finish the steps that do not depend on it, and end the run. Never guess a value to keep going, and
  never mark a step done whose Expect did not match. Why: a wrong guess costs a review round and hides the
  real gap; a precise question costs one answer. Test: a spec whose anchor text is missing from the file; the
  report has a question for that step, the file is unchanged, and the step is marked blocked.
- [invariant] Apply `know-your-limits` for the whole run when it is installed: nothing from memory, names
  looked up, one step then its check, read errors in full. Test: the transcript shows each step's Check run
  before the next step's edit.

## Procedure for the author

1. Fit: the task is outsourceable when its design is settled, it can be cut into steps you can write down,
   and a test can say whether it works. If not, plan or investigate first, or do it yourself.
2. Plan: run `feature-planning` at the depth its tiers ask for and get the owner's approval when the plan
   needs it. Write down every name, signature and file path the executor will need.
3. Tests: write the acceptance tests, see them fail for the right reason, commit them, and hash them with
   `python3 scripts/check_handoff.py hash [test files]`.
4. Spec: copy `references/spec-template.md` to `docs/handoff/[spec-id]/SPEC.md`, one spec per package. Set
   Base to the full commit SHA that contains the tests. Fill every section; quote, do not point.
5. Lint: `python3 scripts/check_handoff.py lint docs/handoff/[spec-id]/SPEC.md` until no error. Treat H09
   and H10 warnings as questions to yourself.
6. Cold read: one small-tier agent, the spec as its only input, the question list as its only output. Fix,
   repeat until it has no question. Set Status to ready and commit the spec.
7. Run: the executor works in its own checkout or worktree at Base, never in yours, with this prompt and
   nothing else: "Read docs/handoff/[spec-id]/SPEC.md and carry it out. The Executor rules in it are binding."
8. Review: `python3 scripts/check_handoff.py verify docs/handoff/[spec-id]/SPEC.md --repo [checkout]`, every
   Acceptance command yourself, the diff against each step, Deviations and Questions.
9. Verdict: accepted (merge per `commit-hygiene`, Status accepted), changes (next round per the rules), or
   needs-human (after the cap, or when a question is the owner's to answer).

## Traps

- A step that says "update the tests accordingly": the executor now owns the definition of done.
- A Context section that quotes code from memory instead of from the file at Base; the anchor is then missing
  and the executor stops, correctly, on step one.
- Base set to a branch name; it moves, and the quoted text no longer matches. Use the SHA.
- One spec for the whole feature; the executor loses the early steps by the time it reaches the late ones.
- Answering an executor question in chat; the next run never sees it.
- A cold read done by the author's own session; it has the same blind spots as the author.
- The executor running in the author's checkout, where its stray edits mix with yours.

## Done when

- The spec lints without error, a cold read found no open question, and Status was ready before the run.
- The protected tests are unchanged, `verify` reports no error, and you ran every Acceptance command yourself.
- The verdict is recorded in the spec's Status, and every review failure was classed as spec gap or executor
  error.

## References

- [references/spec-template.md](references/spec-template.md): load at step 4; the spec layout with the
  canonical Executor rules block.
- `scripts/check_handoff.py`: `lint`, `verify`, `hash`, `rules`; run with `--help` for the codes.

## Sources

- https://code.claude.com/docs/en/best-practices: "Write a specific prompt", "Give Claude a check to run" and
  "Review against your spec", verified 2026-11-08.
