---
name: agent-toolbelt
description: "Picks the cheapest tool that answers a question and keeps the working context small: file-name and text search before reading, jq for JSON, structural search, git history search, gh for GitHub objects, type checker or language server for symbols, docs index tool, parallel calls, scoped subagents. Use when exploring a repo or choosing a tool. Not for what to claim (evidence-before-claims)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Agent toolbelt

This skill decides which tool a coding agent reaches for first, how many calls it makes at once, when it hands
work to a subagent, and how it keeps its context small. Tool manuals stay with their authors: the reference
lists only the flags that were checked, with their sources. Whether a finding may be stated as fact stays with
`evidence-before-claims`, and which actions may leave the machine stays with `safe-actions`. The failure it
prevents: whole files read to answer a one-line question, a guessed flag that silently does something else, and
a subagent's confident summary treated as a result.

## Applies when / does not apply

- Applies: you explore an unfamiliar repository, look for where something is defined or used, need a fact from
  JSON, git history or a GitHub object, plan several lookups, consider delegating to a subagent, or notice the
  context filling up with output you will not use.
- Does not apply: deciding whether a claim is verified, reported or inferred (`evidence-before-claims`);
  classifying an action as allowed, approval or never (`safe-actions`); proving a change works
  (`verify-before-done`); the technique of UI measurement (`browser-verification`, plugin web).

## Rules

- [invariant] Exploration is read-only. Do not delete, overwrite, reset, clean, install, migrate or call a
  non-local service to find something out. A rewrite tool runs in preview mode first. Why: a command that
  answers a question and also changes state turns a lookup into an incident. Test: ask the agent to find
  unused files and to preview a bulk rename; it lists and diffs, and `git status` shows no change afterwards.
  The ast-grep `run --rewrite` command shows a diff, and only `--update-all` (`-U`) applies it without
  confirmation. Source: https://ast-grep.github.io/guide/rewrite-code.html and the ast-grep CLI reference at
  https://ast-grep.github.io/reference/cli.html (verified 2026-11-01). Anything that leaves the machine goes
  through `safe-actions`.
- [invariant] A flag, subcommand or output format counts as known only after you checked it in this session:
  run `command -v [tool]` for availability, then the tool's `--help`, or read its vendor docs for the installed
  version. If neither is possible, say "unverified" and use a form you did verify. Why: an invented flag
  either errors or, worse, means something else. Test: asked to use `rg --sort-by-relevance`, the agent runs
  `rg --help` or the docs lookup, finds no such flag, and says so instead of running it. If `rg` is absent it
  says that and falls back to another search. Source: `evidence-before-claims` for the rule; the verified
  flags are in the reference.
- [invariant] A subagent's report is a lead, not a result. Re-run the decisive check yourself (open the file,
  run the search, run the command) before the report carries a decision, a deletion or a claim to the user.
  Why: a subagent reports from a partial view and states it fluently. Test: a subagent says "function X has no
  callers"; before deleting X, the agent runs its own search for X and finds or fails to find a caller.
  Source: `evidence-before-claims` (reported claims are checked before they carry a decision).
- [default] Use the cheapest tool that can answer the question, in this order: a file-name or text search
  (such as ripgrep) to locate; a ranged read of the located lines; a structural, type-aware or history tool
  when the question is about structure, symbols or past changes; a subagent or a browser last. Trade-off: the
  cheap tool can miss what a deeper one finds (a symbol built by string concatenation, a generated file
  ignored by `.gitignore`), so widen the search when a result looks too small. Deviate only with an ADR that
  names this trade-off. Source: ripgrep ignores files matched by `.gitignore`, hidden files and binary files
  by default, https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md (verified 2026-11-01).
- [default] Query structured data with a structured tool: `jq` for JSON, `gh` with `--json` and `--jq` for
  GitHub objects, the package manager's own JSON output for dependency data. Do not read a large JSON file
  into context to find one field. Trade-off: a query must be written and checked; a wrong filter returns
  nothing or the wrong field, so test it on a known record. Deviate only with an ADR that names this
  trade-off. Source: https://jqlang.github.io/jq/manual/ and https://cli.github.com/manual/gh_pr_view
  (verified 2026-11-01).
- [default] Use a structural search such as ast-grep when the question is about code shape (every call with a
  given argument pattern, every function of a form) and a text search would drown in comments, strings and
  whitespace variants. Use plain text search for names and literals. Trade-off: it needs the language
  parser and a pattern that is easy to get subtly wrong, so check the first matches by eye. Deviate only with an
  ADR that names this trade-off. Source: https://ast-grep.github.io/guide/quick-start.html (structural
  patterns match AST nodes instead of text, verified 2026-11-01).
- [default] Ask history questions of the history. `git log -S[text]` finds commits that changed how often a
  string occurs, `git log -G[regex]` finds commits whose diff lines match, `git log -L` follows a line range
  or a function, and `git blame` shows who last changed each line, with `-w`, `-M` and `-C` to look past
  whitespace and moved code. Trade-off: blame names the last change, not the cause, so read the commit message
  and its diff before drawing a conclusion. Deviate only with an ADR that names this trade-off. Source:
  https://git-scm.com/docs/git-log and https://git-scm.com/docs/git-blame (verified 2026-11-01).
- [default] Ask the type checker, compiler or language server about symbols, types and references when one is
  configured for the project, instead of inferring them from text. Trade-off: it needs a working build or
  configuration and can lag behind unsaved edits. Deviate only with an ADR that names this trade-off.
  Source: none; design judgment.
- [default] For library and framework facts use a documentation index tool when one is available (for example
  Context7: resolve the library, then query it), otherwise the vendor docs for the installed version.
  Training memory is not a source. The labelling of what you found follows `evidence-before-claims`.
  Trade-off: a lookup costs a call and an index can lag the newest release, so check the version it covers.
  Deviate only with an ADR that names this trade-off. Source: `evidence-before-claims`.
- [default] For facts about a rendered page (layout, colour, console errors, what a user sees) use a headless
  browser and measure; the method is in `browser-verification`. Do not infer UI facts from templates.
  Trade-off: starting a browser and a served build is slower than reading code. Deviate only with an ADR that
  names this trade-off. Source: `browser-verification`.
- [default] Make independent calls in the same step: several searches, several file reads, several `gh` queries
  that do not use each other's output. Run dependent calls in order. Trade-off: parallel output arrives
  together and can be large, and parallel writes to the same file or the same service can collide, so
  parallelise reads only. Deviate only with an ADR that names this trade-off. Source: none; design judgment.
- [default] Keep context small. Read the lines you need by range, limit match counts (`rg -m`), list file names
  (`rg -l`, `rg --files`) before opening contents, and summarise a large output in a line or two instead of
  pasting it. Say where the full output is if you saved it. Trade-off: a summary loses detail you may need
  later, so keep the command that produced it. Deviate only with an ADR that names this trade-off. Source:
  https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md (`-l`, `--files`, `-m` options; verified
  2026-11-01) and https://code.claude.com/docs/en/sub-agents (side tasks that flood the conversation with search
  results or logs belong in a separate context; verified 2026-11-01).
- [default] Delegate to a subagent only when the task is separable and its output would otherwise flood the
  main context (a wide search, a long log, a large file set). Give it a written brief: the question, the scope
  (paths, sources, tools it may use), a budget (number of files or calls, or a time limit), what it must not
  do (no writes, no external calls unless stated), and the definition of the result (a list with file and
  line, a yes or no with the evidence). Trade-off: a subagent adds cost and a hand-off that loses nuance, and
  it sends its own requests against the same usage limits. Deviate only with an ADR that names this
  trade-off. Source: https://code.claude.com/docs/en/sub-agents (a subagent runs in its own context window and
  returns only the summary; its requests count toward the same usage limits; verified 2026-11-01).

## Procedure

1. State the question in one line and what a complete answer looks like.
2. Check what is installed: `${CLAUDE_SKILL_DIR}/scripts/toolcheck.sh` lists `rg`, `jq`, `fd`, `ast-grep`, `gh`,
   `git`, `node` and `python3` with versions. It only reads and always exits 0. Without the script, use
   `command -v [tool]`.
3. Pick the first rung of the ladder in
   [references/tool-ladder.md](references/tool-ladder.md) that can answer. Use only flags listed there as
   checked, or check the flag with `--help` first.
4. Batch independent lookups into one step. Read ranges, not files.
5. If the result is empty or suspiciously small, widen: check ignore rules, other spellings, generated code,
   other languages in the repository.
6. If a subagent is justified, write the brief from
   [references/delegation-brief.md](references/delegation-brief.md), send it, and plan how you will check the
   answer.
7. Before using a result, confirm it with a second, independent look when it will drive a deletion, a rename
   or a statement to the user.
8. Report what you ran in short form: the command, the count, the files, so the user can repeat it.

## Traps

- `rg` finds nothing because the file is git-ignored, hidden or binary; the file exists.
- On Linux `sg` is usually a different program (setgroups), so a call to `sg` meant as ast-grep does something
  unrelated. Use `ast-grep` by its full name.
- A `jq` filter that returns `null` because the key is spelled differently, read as "the field is empty".
- `git log -S` and `-G` look at diffs, not at the current tree; a string that moved without change in count
  does not appear.
- `git blame` points at a reformatting commit; ignore whitespace with `-w` and follow moves with `-M` and `-C`.
- Reading a 4,000-line file to find one function.
- A subagent told to "look into the auth code" with no scope, no limit and no result format.
- Running a bulk rewrite with the apply flag as a way to see what it would change.
- Parallel calls that write to the same file.

## Done when

- The answer came from the cheapest tool that could give it, and the command or query is on record.
- Every flag used was checked this session or marked unverified.
- Independent lookups ran together, and no whole file was read for a range.
- Any subagent had a written scope, budget and result definition, and its claims were re-checked by you.
- Nothing was changed, deleted or contacted outside the working tree to explore.

## References

- [references/tool-ladder.md](references/tool-ladder.md): read when you choose a tool or need the checked flags
  for `rg`, `jq`, `ast-grep`, `git` and `gh`.
- [references/delegation-brief.md](references/delegation-brief.md): read when you consider handing work to a
  subagent or when you receive its report.

## Sources

- https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md: default filtering, `--files`, `-g`, `--type`,
  verified 2026-11-01.
- https://jqlang.github.io/jq/manual/ and the `jq --help` output of jq 1.7 run in this session: `-e`, `-r`,
  `-c`, `-n`, `--arg`, verified 2026-11-01.
- https://ast-grep.github.io/guide/quick-start.html and https://ast-grep.github.io/guide/rewrite-code.html:
  structural patterns, `sg` name clash on Linux, rewrite preview and `-U`, verified 2026-11-01.
- https://git-scm.com/docs/git-log and https://git-scm.com/docs/git-blame: `-S`, `-G`, `-L`, `-w`, `-M`, `-C`,
  verified 2026-11-01.
- https://cli.github.com/manual/gh_pr_view: `--json`, `--jq`, `--comments`, verified 2026-11-01.
- https://code.claude.com/docs/en/sub-agents: separate context, summary-only return, shared usage limits,
  verified 2026-11-01.
