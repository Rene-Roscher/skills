# tools

`lint.py` checks the repository. It needs Python 3 (tested on 3.12) and nothing outside the standard library.

```bash
python3 tools/lint.py                              # whole repository
python3 tools/lint.py --commits origin/main..HEAD  # also check commit messages
python3 tools/lint.py --strict                     # warnings fail too
python3 tools/lint.py --help
```

Each finding prints as `path:line: error|warning ID message`. The run exits 1 when there is an error.

| ID | Checks |
|---|---|
| L00 | Plugins have skills (warning while a plugin is empty); `docs-tools` has none |
| L01 | Frontmatter starts on line 1, block-style YAML, quoted values |
| L02 | Allowed frontmatter keys and their order |
| L03 | `name` format, length, equal to the directory name |
| L04 | `description` length, no angle brackets, a "Use when" clause |
| L05 | `license: Apache-2.0` in skills and plugin manifests, root LICENSE and NOTICE |
| L07 | Body length, links stay inside the skill, every reference file linked, references one level deep |
| L08 | Rule tags carry `Test:` or `Trade-off:` and the ADR clause; `## Sources` present; no `[opinion]` under `plugins/` |
| L09 | No personal or absolute paths |
| L10 | No download piped into a shell |
| L11 | No instructions fetched from a URL, no dynamic-context blocks |
| L13 | No IP addresses outside the documentation ranges, no emails outside example domains, no 40-character hex strings outside `.github/workflows/` |
| L14 | No private terms |
| L15 | CVE and issue claims carry a URL |
| L16 | No build markers or template placeholders under `plugins/` |
| L17 | No AI attribution in files or commit messages |
| L18 | Marketplace entries match plugin manifests, semver versions, CHANGELOG headings, install line in each README, cross-marketplace dependencies allowlisted |
| L19 | No hooks, `bin/`, `.mcp.json` or `CLAUDE.md` in plugins |
| L20 | Eval cases have a prompt, a grader and valid tags |
| W01 | Filler words (warning) |

## Private terms

Put one term per line in `.denylist.local` at the repository root. The file is gitignored. CI reads the same
list from the `SKILLS_DENYLIST` secret. A hit prints the term's index, never the term, because CI logs are
public. Lines starting with `#` are comments.

## Inline exceptions

A line may carry `<!-- lint-allow: ID reason -->`, on the line itself or the line before. The reason is
required. Under `plugins/` only L09, L10, L11 and L13 can be allowed this way.
