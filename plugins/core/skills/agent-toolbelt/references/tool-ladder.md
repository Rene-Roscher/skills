# Tool ladder and checked flags

Load when you choose a tool, or need the checked flags for `rg`, `jq`, `ast-grep`, `git` and `gh`.

## Contents

- The ladder
- ripgrep
- jq
- ast-grep
- git history
- gh
- Documentation, types, browser
- What was checked and what was not

## The ladder

| Question | First tool | Then |
|---|---|---|
| Which files exist for X? | file-name listing (`rg --files`, `fd` if installed, `git ls-files`) | read the best match by range |
| Where is the string or name X? | text search (`rg`) | ranged read of the hits |
| Every call or declaration of a given shape? | structural search (`ast-grep`) | check the first matches by eye |
| What does this JSON say? | `jq` | none; do not open the file whole |
| Who changed this and why? | `git log -S/-G/-L`, `git blame` | read the commit message and diff |
| What is on this PR or issue? | `gh ... --json --jq` | open the diff only for files you need |
| What type or signature is this, who references it? | type checker or language server | text search as a cross-check |
| How does library L behave in version V? | documentation index tool, else vendor docs | `evidence-before-claims` for labelling |
| What does the page look like? | headless browser | `browser-verification` |
| A wide search that would flood context | scoped subagent | re-check its answer yourself |

Check availability once per session with `${CLAUDE_SKILL_DIR}/scripts/toolcheck.sh` or `command -v [tool]`. When
a tool is missing, say so and use the next rung. Do not install tools without approval (see `safe-actions`).

## ripgrep

Checked: the GUIDE and the flag definitions in the ripgrep repository, https://github.com/BurntSushi/ripgrep
(guide: GUIDE.md; flags: crates/core/flags/defs.rs), verified 2026-11-01. The binary itself was not installed
in this session, so run `rg --help` before relying on a flag in your version.

- Default filtering: it skips files matched by `.gitignore`, `.ignore` and `.rgignore`, hidden files and
  directories, binary files, and does not follow symlinks. `-u` lowers filtering one step per repetition;
  `-uuu` searches ignored, hidden and binary files too.
- `-n` / `--line-number`, `-l` / `--files-with-matches`, `-c` / `--count`, `-m` / `--max-count NUM` (matching
  lines per file), `-g` / `--glob`, `-t` / `--type`, `-C` / `--context`, `--files` (list the files that would
  be searched), `--json`, `-F` / `--fixed-strings`, `-w` / `--word-regexp`, `-i` / `--ignore-case`.
- Exit status: 0 when there is a match, 1 when there is none and no error, 2 on error. Source:
  the ripgrep man page template, crates/core/flags/doc/template.rg.1.
- Quote globs and patterns so the shell does not expand them.

Typical: `rg -n -g '*.py' 'def parse_amount'` to locate; `rg -l 'TODO(owner)' --type js` to list files.

## jq

Checked: `jq --help` of jq 1.7 in this session and the manual at https://jqlang.github.io/jq/manual/
(verified 2026-11-01).

- `-r` raw strings, `-c` compact output, `-n` no input, `-e` exit status from the last output, `--arg name
  value` (always a string), `-f file` filter from file.
- `-e` exits 1 if the last output is `false` or `null` and 4 if there was no output. Use it in checks.
- Test the filter on one known record before running it on the whole file. A misspelled key yields `null`,
  not an error.

Typical: `jq -r '.dependencies | keys[]' package.json`.

## ast-grep

Checked: https://ast-grep.github.io/guide/quick-start.html, https://ast-grep.github.io/guide/rewrite-code.html
and https://ast-grep.github.io/reference/cli.html (verified 2026-11-01). The tool was not installed in this
session, so check `ast-grep --help` before relying on a flag in your version.

- The command is `ast-grep`; `sg` is an alias that clashes with the Linux `sg` (setgroups) tool.
- `run` flags: `-p` / `--pattern`, `-l` / `--lang`, `-r` / `--rewrite`, `--json[=pretty|stream|compact]`
  (the `=` is required), `-A` / `-B` / `-C` context, `--globs`, `--no-ignore`, `-i` / `--interactive`,
  `-U` / `--update-all`.
- A `--rewrite` run prints a diff; the files change only with `--interactive` and confirmation, or with
  `-U`. During exploration, never pass `-U`.
- Without `--lang`, the language is inferred from the file extension.

Typical: `ast-grep run -p 'console.log($$$ARGS)' -l ts src` (`$$$ARGS` matches zero or more nodes, per
https://ast-grep.github.io/guide/pattern-syntax.html, verified 2026-11-01).

## git history

Checked: https://git-scm.com/docs/git-log and https://git-scm.com/docs/git-blame, and `git log --help` of
git 2.43 in this session (verified 2026-11-01).

- `git log -S'text'`: commits that change the number of occurrences of the string. Add `--pickaxe-regex` to
  treat it as a regex.
- `git log -G'regex'`: commits whose patch has added or removed lines matching the regex.
- `git log -L :funcname:path` or `-L start,end:path`: how a function or line range evolved; implies a patch;
  no pathspec limiters.
- `git blame -L start,end path`: last change per line in a range; `-w` ignores whitespace changes, `-M`
  detects moved lines, `-C` detects copied lines.
- Add `--oneline` for a short listing.

Typical: `git log -S'retry_limit' --oneline -- src/` then `git show [commit]` for the one you need.

## gh

Checked: https://cli.github.com/manual/gh_pr_view and the `gh --help`, `gh pr view --help` and `gh api
--help` output of gh 2.45 in this session (verified 2026-11-01).

- `gh pr view [number|url|branch] --json fields --jq expression`; `--comments` for the comments and
  reviews. The field list is in the manual page.
- `gh api path --jq expression`; `--paginate` fetches all pages; the default method is GET.
- Reading is fine. Creating, editing, merging, commenting or closing leaves the machine and follows
  `safe-actions`.

## Documentation, types, browser

- Documentation index tool (for example Context7): resolve the library name to an id, then query that id with a
  specific question; mention the version you need. If none is available, read the vendor docs for the version
  in the lockfile.
- Type checker or language server: run the project's configured one (the project docs say which). It answers
  "what is the type" and "who references this" better than text search.
- Headless browser: see `browser-verification`.

## What was checked and what was not

Checked in this session: the flags marked above for `jq`, `git`, `gh` (installed here), and for ripgrep and
ast-grep from their repositories and docs (not installed here). Not checked: `fd` flags (not installed here,
not documented in this skill beyond the name). Use `fd --help` if you rely on it.
