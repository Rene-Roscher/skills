# Lesson stores per environment

Load when choosing or setting up where lessons live, or when moving lessons between tools. Facts verified
against the vendor docs on 2026-10-31; re-check the installed version before relying on a version-bound detail.

## Contents

- Claude Code
- AGENTS.md
- Laravel Boost
- Fallback: docs/lessons/
- Project facts
- Moving a lesson

## Claude Code

Source: https://code.claude.com/docs/en/memory.

Instruction files, written by people and loaded every session:

| File | Scope | Use for lessons |
|---|---|---|
| `./CLAUDE.md` or `./.claude/CLAUDE.md` | team, committed | short "always do X" lessons for the whole repo |
| `.claude/rules/*.md` | team, committed | one topic per file; `paths:` frontmatter loads it only when Claude reads or writes a matching file |
| `./CLAUDE.local.md` | you, this project, gitignored | personal project notes |
| `~/.claude/CLAUDE.md`, `~/.claude/rules/` | you, every project | personal working preferences |

- Files above the working directory load at launch; files in subdirectories load when Claude reads a file
  there. All found files are concatenated, closest last.
- `@path` imports a file into CLAUDE.md. Paths resolve relative to the importing file, up to four hops. An import
  does not reduce context cost. A path inside backticks is not imported.
- Target under 200 lines per CLAUDE.md. Move file-specific lessons into path-scoped rules.
- The project-root CLAUDE.md is re-read after `/compact`; nested files and path-scoped rules load again on
  demand.

Auto memory, written by Claude:

- Location `~/.claude/projects/[project]/memory/`: a `MEMORY.md` index plus one file per memory. One directory
  per git repository, shared by its worktrees, machine-local.
- The first 200 lines or 25KB of `MEMORY.md` load at session start; topic files are read on demand.
- Frontmatter `type` is one of `user`, `feedback`, `project`, `reference`. Claude Code adds a `modified`
  timestamp when it writes a file with frontmatter.
- On by default in local sessions, off by default in self-hosted environments. Toggle in `/memory`
  (`autoMemoryEnabled`), or set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- Subagents do not get the main conversation's auto memory. A subagent with the `memory` field gets its own
  directory; `project` scope is `.claude/agent-memory/[agent-name]/`.
- `/memory` lists and opens the files. `/context` shows what loaded.

Choose: a lesson only you need goes to auto memory or `~/.claude/`. A lesson the team needs goes to CLAUDE.md
or `.claude/rules/`, reviewed in a pull request.

## AGENTS.md

Sources: https://agents.md/ and the AGENTS.md section of the Claude Code memory docs.

- Plain Markdown, no required fields. One at the repo root, more in subprojects; the closest file to the edited
  file wins, and explicit chat prompts override it.
- Read by many agents (the site lists Codex, Cursor, Gemini CLI, GitHub Copilot coding agent, Jules, Aider,
  Zed and others).
- Claude Code (v2.1.277 or later) reads `AGENTS.md` by default only when no `CLAUDE.md`, `.claude/CLAUDE.md` or
  `CLAUDE.local.md` exists in the working directory or above it. To share one file across tools, keep the
  lessons in `AGENTS.md` and put `@AGENTS.md` at the top of `CLAUDE.md`.
- A `CLAUDE.local.md` counts as a CLAUDE.md for that check, so adding one switches `AGENTS.md` off for you.

## Laravel Boost

Source: https://laravel.com/docs/13.x/boost. The 12.x page of the same docs lists no Record Rule tool, so check
the MCP tool list of the installed Boost before relying on `record-rule`.

- `.ai/rules/`: project rules as Markdown with `paths:` globs in frontmatter, plus `.ai/rules/index.md` that
  maps globs to rule files. Committed. Agents are told to consult the index before planning or editing.
- Record a rule through the `record-rule` MCP tool (`glob`, `title`, `note`). It files the rule and regenerates
  the index. A hand-written rule file is not discovered until the index is regenerated.
- `BOOST_RULES_ENABLED=false` removes the tool and stops Boost from managing `.ai/rules`.
- `.ai/guidelines/*.md` or `*.blade.php`: custom guidelines merged into the generated guideline files on
  `boost:install`.
- Generated `CLAUDE.md` and `AGENTS.md`: Boost replaces only the content inside its `laravel-boost-guidelines`
  block, and the docs say these files may be gitignored because they are regenerated. A team lesson written
  there can be lost on the next update or never committed.

Map: a Boost project rule is a team lesson. Put the rule sentence and the Why into the `note`, and the trigger
into the `glob`.

## Fallback: docs/lessons/

Use when the environment has no memory feature, or when several tools must share lessons.

```text
docs/lessons/
├── INDEX.md                      # one line per lesson
├── formatter-own-files-only.md
└── money-integer-cents.md
```

- `INDEX.md` lines: a line per lesson: title in square brackets, the file name in parentheses, then when it applies. Keep it under 200 lines.
- Link it from the instruction file. For Claude Code: `@docs/lessons/INDEX.md` in CLAUDE.md. For other agents:
  a line in AGENTS.md such as "Before acting, read docs/lessons/INDEX.md and open the lessons that match the
  files you touch."
- Commit the directory and review lesson changes like code.
- `check_lessons.py docs/lessons` finds `INDEX.md` on its own.

## Project facts

Facts are what any teammate needs whether or not an agent is involved: how to build and test, ports, service
names, versions pinned in production, where config and secrets are managed, architecture boundaries. Put them in
`docs/PROJECT-FACTS.md` (or the specs and README the project already has) and link them from lessons.

Test for the split: would a new human teammate need this sentence? Then it is a fact. Is it about what an agent
tends to get wrong, or which check to run before a step? Then it is a lesson.

## Moving a lesson

- Personal to team: the lesson turned out to be about the codebase. Move it into the repo store, keep the Why,
  delete the personal copy.
- Store to artifact: the lesson recurred. Build the artifact (`references/promotion.md`) and leave a short
  pointer lesson.
- Between tools: copy rule, Why and How to apply; adapt the trigger syntax (`paths:` in Claude Code rules and
  Boost rules, nearest-file scope in AGENTS.md).
