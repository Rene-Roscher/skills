---
name: learning-loop
description: "Stops an agent from repeating a mistake. After a correction or a non-obvious trap it records a lesson (rule, Why, How to apply, links) in the project's durable memory, checks lessons before acting, promotes a recurring lesson into a test, lint rule, hook or CI gate, and fixes or deletes stale ones. Use when corrected, after a surprising failure, or when told to remember. Not for specs or ADRs."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Learning loop

This skill turns a correction into a durable lesson, and a lesson that recurs into a check that fails. It
decides what gets recorded, where it lives in the current environment, what shape it has, when it must become
an enforcing artifact and when it is deleted. Facts about the system itself belong to project docs and specs.
The failure it prevents: the user corrects the same mistake again next week, because the first correction
lived only in a chat that no longer exists.

## Applies when / does not apply

- Applies: the user corrects an action or an output; the user confirms a non-obvious approach that should be
  repeated; a failure had a cause the code did not show (a tool default, an environment difference, a test that
  passed for the wrong reason); the user says "remember", "from now on", "next time" or "again"; a lesson turns
  out wrong or outdated; work starts in an area that already has lessons; someone sets up where agent lessons
  live.
- Does not apply: writing specs, ADRs, onboarding guides or READMEs; a preference that only concerns the current
  task; general questions that involve no project memory. Completion claims belong to `verify-before-done`,
  facts about dependencies to `evidence-before-claims`.

## Rules

Most important first. Examples use an invoicing app and a booking system.

- [invariant] Write the lesson before you continue the task, into the durable store of this environment. "Noted,
  I will keep that in mind" is not a lesson. Why: every session starts with a fresh context, and an instruction
  given only in conversation is gone after compaction or in the next session. Test: after a correction, the
  trace shows a write to the lesson store before the next task step (eval `output-records-correction`). Source:
  Claude Code memory docs: "If an instruction disappeared after compaction, it was given only in conversation
  [...] Add conversation-only instructions to CLAUDE.md to make them persist."
  (https://code.claude.com/docs/en/memory, verified 2026-10-31).
- [invariant] Lessons never hold secrets, credentials, tokens, connection strings, personal data or customer
  data. Record where a value lives (the variable name, the secret manager path, the runbook), never the value,
  and reduce a customer incident to its mechanism. Why: lesson stores load into every session, and team stores
  are committed, so a pasted value reaches every teammate, tool and clone. Test:
  `python3 ${CLAUDE_SKILL_DIR}/scripts/check_lessons.py [store]` reports no secret-shaped string; asked to
  remember a password, the agent stores a pointer and not the password (eval `adversarial-secret-in-lesson`).
  Source: Laravel Boost docs: project rules "should be committed to source control"
  (https://laravel.com/docs/13.x/boost, verified 2026-10-31); Claude Code memory docs: project CLAUDE.md reaches
  "Team members via source control" (verified 2026-10-31).
- [invariant] Check lessons before acting. The index is loaded, the lesson bodies are not: before you edit,
  run a command or answer in an area, search the index and the store for the files, tools and commands in play,
  open every matching lesson and apply its How to apply. Why: an index line names the trap but rarely carries
  the check. Test: with a store whose lesson covers the task, the agent reads that lesson before its first edit
  and follows it (eval `output-check-before-acting`). Source: Claude Code memory docs: "Claude Code doesn't load
  topic files [...] at startup. Claude reads them on demand" (verified 2026-10-31).
- [invariant] One trap, one lesson. Search the store before writing, update the lesson that already covers the
  trap, and resolve a contradiction by editing or deleting the wrong lesson, never by adding a third. Why: "if
  two instructions contradict each other, Claude may pick one arbitrarily." Test: record a correction that an
  existing lesson covers; the diff edits that file and adds none. Source: Claude Code memory docs, Write
  effective instructions (verified 2026-10-31).
- [invariant] A lesson that fires a second time becomes an enforcing artifact: an architecture test or lint
  rule for a code pattern, a permission deny rule or PreToolUse hook for a command that must never run, a
  bootstrap check for an environment mismatch, a CI gate for a rule that spans files. The lesson then keeps its
  Why and shrinks to the trigger plus a pointer to the artifact. Why: memory and instruction files are context,
  not enforcement. Test: reintroduce the mistake in a scratch change; the artifact fails, and passes again after
  the revert. Source: Claude Code memory docs: "Claude treats them as context, not enforced configuration. To
  block an action regardless of what Claude decides, use a PreToolUse hook instead." and the recurrence trigger
  "Claude makes the same mistake a second time"; hooks docs: exit code 2 on PreToolUse "Blocks the tool call"
  (https://code.claude.com/docs/en/hooks); both verified 2026-10-31.
- [invariant] Fix or delete a stale lesson when you meet the contradiction. When code, config or a newer
  decision disagrees with a lesson, follow the code, say so, and either correct the lesson in place with the
  date and reason or delete it with its index line. A lesson that records a state ("not deployed yet") carries a
  date and goes when the state ends. Why: a stale lesson is obeyed with the authority of a rule, and code
  outranks memory notes (`evidence-before-claims`). Test: a lesson says the project uses npm while the repo has
  `pnpm-lock.yaml`; the agent uses pnpm, reports the drift and edits or deletes the lesson. Source: Claude Code
  memory docs: review instruction files "periodically to remove outdated or conflicting instructions"; Claude
  Code writes a `modified` timestamp into memory frontmatter (verified 2026-10-31).
- [invariant] Keep the always-loaded index inside its load limit: one line per lesson, detail in the lesson
  file. Claude Code loads the first 200 lines or 25KB of `MEMORY.md`, whichever comes first, and drops the rest
  at load. Why: a lesson past the limit exists on disk and never reaches the agent. Test: `check_lessons.py`
  fails on an index over 200 lines or 25,000 bytes. Source: Claude Code memory docs, How it works (verified
  2026-10-31).
- [invariant] Pass the lessons that apply into every delegation brief. Why: "The main conversation's auto
  memory isn't loaded into subagents", so a subagent repeats the mistake the main session already learned. Test:
  a brief for a subagent working on invoice amounts quotes the How to apply of the money lesson. Source: Claude
  Code memory docs (verified 2026-10-31). Brief format: `agent-toolbelt`.
- [default] Facts go to docs, behaviour goes to lessons. A fact holds for anyone working on the system
  (commands, ports, versions, architecture, where config lives) and belongs in `docs/PROJECT-FACTS.md`, a spec,
  the README or AGENTS.md. A lesson is about how to work: what to check, what never to do, which default
  misleads. A lesson links to the fact instead of restating it. Trade-off: two places to look, in exchange for
  facts with one owner that do not drift in copies. Deviate only with an ADR that names this trade-off. Source:
  Claude Code memory docs: auto memory "skips anything it can derive from the codebase [...] It also skips
  anything your CLAUDE.md files already say." (verified 2026-10-31).
- [default] Lesson shape: one file per lesson; frontmatter `name`, a one-line `description` that says when it
  applies, and `type` (`feedback` for behaviour, `project` for dated decisions and ongoing work, `reference` for
  where to find things, `user` for personal preferences); body with the rule in one or two sentences,
  `**Why:**` with the concrete incident in abstract form, `**How to apply:**` naming the trigger (file pattern,
  tool, command) and the check, then links to related lessons. "Be careful with dates" is not a lesson.
  Trade-off: a few minutes per lesson, in exchange for lessons that can be checked, found and pruned. Deviate
  only with an ADR that names this trade-off. Source: Claude Code memory docs: the four `type` values and
  "Write instructions that are concrete enough to verify" (verified 2026-10-31). Proof: `check_lessons.py`
  fails on a feedback lesson without Why or How to apply.
- [default] Store by environment and audience. A lesson about the codebase that the team needs goes into the
  repository; a personal working preference goes into personal memory. Trade-off: team lessons are reviewed in
  pull requests, which is slower than a private note. Deviate only with an ADR that names this trade-off.
  Source: Claude Code memory docs: "Auto memory is machine-local [...] Files are not shared across machines or
  cloud environments."; agents.md: "The closest AGENTS.md to the edited file wins"; Laravel Boost 13.x docs,
  Project Rules; all verified 2026-10-31.

| Environment | Personal lessons | Team lessons |
|---|---|---|
| Claude Code | auto memory: `MEMORY.md` index plus one file per lesson | `CLAUDE.md`; `.claude/rules/*.md`, with `paths:` for file-scoped lessons |
| Other agents (Codex, Cursor, Gemini CLI, Copilot agent) | the tool's own memory, if it has one | `AGENTS.md`, nested per subproject |
| Laravel with Boost that offers `record-rule` | none | `.ai/rules/`, written through the `record-rule` tool, committed |
| No memory feature | none | `docs/lessons/` with `INDEX.md`, linked from the instruction file |

## Procedure

1. Gate: is there a correction, a confirmed non-obvious approach, a trap the code did not show, or an explicit
   "remember"? If not, stop.
2. Screen: remove secrets, personal and customer data. Reduce the incident to its mechanism.
3. Classify: fact (to docs) or lesson; personal or team. Pick the store from the table above.
4. Search the store for the tool, the file pattern and the error text (`rg -i` over the store directory).
   Update a match, or create a new lesson.
5. Write the lesson file, one index line and links in both directions.
6. Recurrence: is this the second time? Build the artifact (see `references/promotion.md`), prove it fails on
   the mistake, and shrink the lesson to the trigger plus a pointer.
7. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_lessons.py [store]` and fix every finding.
8. Tell the user in one line what was recorded and where.
9. On later tasks: search the index, open the matching lessons, check each still holds (fix or delete it if
   not), then act. Quote the lessons that apply in every subagent brief.

## Traps

- An acknowledgment in chat with no write. Nothing reaches the next session.
- A team lesson in auto memory. It is machine-local, so teammates, CI agents and cloud sessions never see it.
- A lesson inside a generated instruction file. Laravel Boost rewrites only the content inside its
  `laravel-boost-guidelines` block on `boost:install` and `boost:update`, and its docs suggest the generated
  files may be gitignored. Put team lessons in `.ai/rules` or `.ai/guidelines`, or outside the block in a
  committed file.
- A hand-written file in `.ai/rules`. Boost's docs say it is not discovered until the index is regenerated;
  record through `record-rule`.
- A `CLAUDE.local.md` added to a project that relies on `AGENTS.md`. With the default setting, Claude Code then
  stops reading `AGENTS.md`.
- Index lines that grow into paragraphs. Entries past line 200 stop loading with no error at session start.
- A lesson that copies a version number, a port or a class name. The source changes and the copy does not.
- A promoted guard that holds only in the test world. A duplicate-order guard read a log table that the suite
  filled synchronously and production filled from a queue seconds later: green suite, duplicates in production.
  Test a guard under the production condition (queue faked or real, production database engine, real clock).
- A rule without its Why. It gets applied to cases it was never about, or dropped as arbitrary.
- A subagent that starts without the lessons. It repeats the mistake the main session learned an hour ago.

## Done when

- The lesson sits in the right store with rule, Why, How to apply, links and one index line.
- `check_lessons.py` passes on the store.
- No second lesson covers the same trap, and no two lessons contradict each other.
- A lesson that recurred names its artifact, and the artifact fails on the mistake.
- Facts found along the way are in project docs, not in lessons.
- The user knows in one line what was recorded and where.

## References

- [references/stores.md](references/stores.md): load when choosing or setting up the store for an environment
  (Claude Code memory and rules, AGENTS.md, Laravel Boost, `docs/lessons/`), or moving lessons between them.
- [references/lesson-format.md](references/lesson-format.md): load when writing or reviewing a lesson or an
  index line. Holds the template, examples and a good-versus-weak table.
- [references/promotion.md](references/promotion.md): load when a lesson recurs and you pick, build and prove
  an enforcing artifact.
- `${CLAUDE_SKILL_DIR}/scripts/check_lessons.py`: run over a lesson store after every write. `--help` lists the
  checks; `--self-test` proves each one fires.

## Sources

- https://code.claude.com/docs/en/memory: CLAUDE.md locations, imports, `.claude/rules/` with `paths`, auto
  memory location, types, index load limit (200 lines or 25KB), on-demand topic files, machine-local storage,
  subagents without main memory, AGENTS.md loading rules, context not enforcement, verified 2026-10-31.
- https://code.claude.com/docs/en/hooks: PreToolUse exit code 2 blocks the tool call, `permissionDecision`
  deny, verified 2026-10-31.
- https://agents.md/: open format, no required fields, nearest file wins, verified 2026-10-31.
- https://laravel.com/docs/13.x/boost: `.ai/guidelines`, `.ai/rules` with `index.md`, the `record-rule` tool,
  `BOOST_RULES_ENABLED`, generated files and the guidelines block, verified 2026-10-31.
- https://laravel.com/docs/12.x/boost: lists no Record Rule tool, so check the installed version, verified
  2026-10-31.
