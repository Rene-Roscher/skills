---
name: maintainable-code
description: "Keeps new code easy to change and review: seams and adapters so it is testable, search the repo before writing, follow neighbouring conventions, duplication before the wrong abstraction, small public surface, explicit errors, dead code and flags removed, small changes, a checklist before adding a dependency. Use when writing, refactoring or reviewing code. Not for test planning (test-strategy)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Maintainable code

This skill decides how new code is shaped so the next person can change it safely: where the seams go, what is
reused and what is left duplicated, which conventions win, and how large a change may be. Language style guides,
linters and framework idioms stay with their own docs, and what to test stays with `test-strategy`. The failure
it prevents: a second way of doing something the repository already does, an abstraction that every new case
bends, and a change too large for anyone to review properly.

## Applies when / does not apply

- Applies: you write a new module, function or class, extend existing code, refactor, review a diff, add a
  dependency, or add a feature flag.
- Does not apply: choosing which tests to write, coverage and flaky tests (`test-strategy`); planning a feature
  (`feature-planning`); proving it works (`verify-before-done`); commit and pull request wording
  (`commit-hygiene`); whether to build or buy at product level (`build-vs-buy`, plugin saas).

## Rules

- [invariant] Before writing a helper, a type, a query or a client, search the repository for one that already
  does the job, and use it or extend it. Report what you searched for. Why: a second implementation drifts from
  the first and the two get fixed separately. Test: ask for a function that formats a date that the repository
  already has in a shared module; the diff imports the existing one and adds none, and the reply names the
  search. Source: none; design judgment.
- [invariant] Read the neighbouring code and the project's own docs (contributing guide, style config, agent
  instructions) before choosing a style, a layout or a pattern, and follow what is there. Why: reviewers
  accept consistency with the codebase when no rule decides, and a second pattern doubles what every reader
  must know. Test: a repository with two controllers that return a response object through one shared helper;
  the new controller uses that helper and does not hand-build the response. Source:
  https://google.github.io/eng-practices/review/reviewer/standard.html (style should be consistent with what
  is there; ask for consistency with the current codebase when no other rule applies; verified 2026-11-01).
- [invariant] Errors are explicit. A failure is returned or raised with the cause and the input that matters, or
  it is handled in a place that can act on it. Never swallow an error with an empty handler, a bare default or
  a log line that hides the failure from the caller. Why: a swallowed error turns into wrong data later, far
  from the cause. Test: make the called dependency fail; the caller gets a distinct error that names the
  operation, and no wrong value is returned or stored. Source: none; design judgment.
- [invariant] Anything that talks to a third party, the clock, the filesystem, randomness or the network is
  reached through a small interface that the caller receives (a parameter or a constructor argument), so a
  test can pass a fake. Why: code that creates its own client cannot be tested without the real service.
  Test: write the unit test for the new code using a fake of that interface; it runs without network access
  and without patching globals. Source: https://alistair.cockburn.us/hexagonal-architecture/ (application
  developed and tested in isolation from run-time devices and databases, through ports and adapters,
  verified 2026-11-01).
- [default] Wrap each third party in one adapter that exposes only what this application needs, in the
  application's own types. Provider names and response shapes do not leak into domain code. Trade-off: one
  more layer to write and keep in step with the provider's API, and a thin pass-through adapter adds nothing.
  Deviate only with an ADR that names this trade-off. Source: https://alistair.cockburn.us/hexagonal-architecture/
  (a technology-specific adapter converts the outside event for the application, verified 2026-11-01).
- [default] Duplicate until the third occurrence, and extract only when the copies change for the same reason.
  Two similar blocks that serve different callers stay apart. When a shared function has collected parameters
  and conditionals for each caller, inline it back into the callers and re-extract from what remains. Trade-off:
  more code in the short term and a fix that must be applied in several places while the copies exist.
  Deviate only with an ADR that names this trade-off. Source: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
  ("duplication is far cheaper than the wrong abstraction"; passing parameters and adding conditional paths
  means the abstraction is wrong; the rule of three itself is a common heuristic and not from that post),
  verified 2026-11-01.
- [default] Keep the public surface small: export only what callers need, prefer one entry point per use case,
  and keep helpers private so they can change without a migration. Trade-off: some code is hard to reach from
  a test and must be tested through the public entry point or moved into its own unit. Deviate only with an
  ADR that names this trade-off. Source: https://martinfowler.com/articles/practical-test-pyramid.html (a
  private method that needs its own test is a sign to split the class; verified 2026-11-01).
- [default] Names say what a thing is or does, long enough to communicate it and no longer. Comments say why the
  code exists or why it is written this way, not what it does. If a comment is needed to explain what, simplify
  the code. Exceptions are regular expressions and complex algorithms. Trade-off: longer names and
  a habit of deleting comments that merely restate the code. Deviate only with an ADR that names this
  trade-off. Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html (naming and
  comments sections, verified 2026-11-01).
- [default] Solve the problem you have now. Do not add parameters, hooks, interfaces or configuration for a
  case nobody has asked for. Trade-off: a later change may need a refactor that a hook would have avoided,
  and you accept that cost instead of paying for guesses. Deviate only with an ADR that names this trade-off.
  Source: https://google.github.io/eng-practices/review/reviewer/looking-for.html (over-engineering: solve the
  problem known now, not one that might arrive; verified 2026-11-01).
- [default] Delete dead code in the change that makes it dead: unused functions, unreachable branches, retired
  flags, commented-out blocks. Version control keeps the history. Trade-off: a deleted block is not in front
  of you when someone asks for it back; use `git log -S` to find it. Deviate only with an ADR that names this
  trade-off. Source: none; design judgment.
- [default] Keep a change to one self-contained purpose, with its tests, and do refactoring in a separate change
  from behaviour changes. Aim for a diff a reviewer can read in one sitting; split larger work into steps that
  each leave the system working. Trade-off: more branches or pull requests and some temporary scaffolding.
  Deviate only with an ADR that names this trade-off. Source:
  https://google.github.io/eng-practices/review/developer/small-cls.html (one self-contained change; separate
  refactorings from features; reviewers may reject a change for size alone; verified 2026-11-01).
- [default] Every feature flag has an owner, a purpose (release, experiment, operations, permission) and a
  removal date or a removal task in the backlog. Release flags are removed once the rollout is complete.
  Trade-off: someone must schedule and do the removal, and a flag that is long-lived must say so. Deviate only
  with an ADR that names this trade-off. Source: https://martinfowler.com/articles/feature-toggles.html
  (flags are inventory with a carrying cost; teams add a removal task or an expiry date; verified 2026-11-01).
- [default] Add a dependency only after the checklist in the reference passes: the need, the standard library
  or an existing dependency as an alternative, maintenance, licence, size and transitive weight, and how it is
  wrapped and removed. Product-level build-or-buy decisions follow `build-vs-buy`. Trade-off: the check takes
  minutes per dependency and sometimes ends in writing ten lines yourself. Deviate only with an ADR that names
  this trade-off. Source: none; design judgment.
- [default] Record a deviation from an existing pattern, a new pattern, or a dependency choice in a short
  architecture decision record (ADR): context, decision, consequences. Small local choices need no ADR.
  Trade-off: a few minutes per decision and a folder to maintain. Deviate only with an ADR that names this
  trade-off. Source: https://adr.github.io/ (an ADR captures one architectural decision and its rationale,
  verified 2026-11-01).

## Procedure

1. Read the project docs and two or three neighbouring files in the area. Note naming, layout, error style,
   and how dependencies are passed in.
2. Search before writing. Read [references/reuse-and-abstraction.md](references/reuse-and-abstraction.md) for
   the search steps and the extract-or-duplicate decision.
3. Design the seams first: list what the new code talks to outside itself and give each a small interface.
4. Write the code in the repository's style. Make errors explicit and the public surface minimal.
5. Remove what your change made dead, including flags that are finished.
6. If you add a dependency, run the checklist in
   [references/dependency-and-change-size.md](references/dependency-and-change-size.md). If the change is
   large, split it by the guidance there.
7. If you deviated from a convention, write the ADR and link it from the change.
8. Review your own diff as a reviewer would: the size, unused code, new patterns, names, comments that restate
   code. Then hand over to `commit-hygiene` for the commit.

## Traps

- A helper copied from another module with small edits, because searching was skipped.
- A shared function whose signature grows a boolean parameter with each new caller.
- A new pattern introduced "because it is cleaner" while three files nearby use the old one, so the codebase now
  has two.
- A thin wrapper around a library that renames methods and adds nothing, while the library's types still leak
  through the rest of the code.
- A try-catch that returns an empty list on any failure.
- A flag that shipped "temporarily" and has three branches of logic hanging off it a year later.
- A refactor mixed into a bug fix, so the fix cannot be reverted without losing the cleanup.
- A dependency added for one function that ten lines would cover, with an unmaintained upstream.

## Done when

- The diff reuses what existed, and the reply names what was searched.
- The new code follows the neighbouring style and introduces no second pattern, or an ADR explains why.
- Everything external is behind an interface the caller supplies, and the new code has a test with a fake.
- No swallowed errors, dead code, speculative parameters or comments that restate code remain.
- Any new flag has an owner and a removal date, and finished flags are gone.
- The change is one purpose, and refactoring is separate from behaviour changes.
- Any new dependency passed the checklist.

## References

- [references/reuse-and-abstraction.md](references/reuse-and-abstraction.md): read when you are about to write
  a helper or when two blocks look alike and you must decide whether to extract.
- [references/dependency-and-change-size.md](references/dependency-and-change-size.md): read when you add a
  dependency, a feature flag, or when a change is growing past one review sitting.

## Sources

- https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction: cost of the wrong abstraction and how to unwind
  it, verified 2026-11-01.
- https://google.github.io/eng-practices/review/reviewer/standard.html: consistency with the codebase,
  verified 2026-11-01.
- https://google.github.io/eng-practices/review/reviewer/looking-for.html: over-engineering, naming,
  comments, verified 2026-11-01.
- https://google.github.io/eng-practices/review/developer/small-cls.html: change size and separate
  refactorings, verified 2026-11-01.
- https://alistair.cockburn.us/hexagonal-architecture/: ports and adapters, verified 2026-11-01.
- https://martinfowler.com/articles/feature-toggles.html: flag categories and removal, verified 2026-11-01.
- https://martinfowler.com/articles/practical-test-pyramid.html: private methods and design, verified 2026-11-01.
- https://adr.github.io/: architecture decision records, verified 2026-11-01.
