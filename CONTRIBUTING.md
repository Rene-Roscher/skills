# Contributing

This file covers where things go, how a skill is written, how it is tested, and how changes are committed and
released. `tools/lint.py` enforces the mechanical rules. A reviewer checks the rest.

## Layout

- `plugins/<plugin>/skills/<skill>/SKILL.md` holds a skill. Detail goes in `references/*.md` next to it.
- `plugins/<plugin>/evals/<skill>/<case>/` holds the eval cases for that skill. Evals do not go inside the skill
  directory.
- `plugins/<plugin>/.claude-plugin/plugin.json` carries the plugin version. Marketplace entries carry none.
- `templates/` holds files that projects copy: `AGENTS.md`, team settings, the project overlay and the example
  profile.
- Plugins ship skills only: no `hooks/`, no `bin/`, no `.mcp.json`, no `CLAUDE.md`.

## Writing a skill

### Frontmatter

```markdown
---
name: example-skill
description: "Decides [what] for [which kind of project]. Use when [situations]. Not for [near misses]."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---
```

- Keys in this order: `name`, `description`, `license`, `compatibility` (only when needed), `metadata`, then
  Claude Code fields.
- `core` and `saas` skills use only the six fields of the Agent Skills specification: `name`, `description`,
  `license`, `compatibility`, `metadata`, `allowed-tools`. Claude.ai uploads and the Skills API reject any other
  field.
- Stack plugins (`laravel`, `web`, `delivery`) may add `paths`, and if a case needs it, `when_to_use`,
  `disable-model-invocation` or `user-invocable`.
- `name` is lowercase letters, digits and single hyphens, at most 64 characters, equal to the directory name, and
  never contains `claude` or `anthropic`.
- `description` is one double-quoted line in the third person. It says what the skill does and when to use it,
  key use case and strongest trigger words first, then "Use when", and ends with a short near-miss boundary where
  one is likely. Aim for 400 characters. Above 500 the lint warns (L21, counting `when_to_use` too), above 1024
  it fails (L04). Claude Code lists every skill description within a budget of 1% of the context window and drops
  the descriptions of the least-used skills first when the listing overflows. No angle brackets: they
  render as entities. Use `[placeholder]`.
- Block-style YAML only. No `[a, b]` or `{a: 1}`, no `---` inside a value, no multi-line scalars. `metadata`
  values are strings and carry no `version`.
- `license: Apache-2.0` in every SKILL.md, because tools that copy a single skill folder leave the repository
  LICENSE behind.
- No `allowed-tools` for now. It pre-approves tools without a prompt.

Sources: https://agentskills.io/specification, https://code.claude.com/docs/en/skills,
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (verified 2026-10-31).

### Body

Sections in this order: a one-paragraph purpose, `## Applies when / does not apply`, `## Rules`,
`## Procedure`, `## Traps`, `## Done when`, `## References`, `## Sources`.

Every rule carries one tag:

```markdown
- [invariant] Rule in one sentence. Why: one line. Test: input, then the expected result.
  Source: https://vendor.example.com/doc (verified 2026-10).
- [default] Rule in one sentence. Trade-off: what you give up. Deviate only with an ADR that names this
  trade-off. Source: https://vendor.example.com/doc (verified 2026-10).
```

- `[invariant]` covers security, correctness, data loss, and the gates a workflow skill is built around. It
  needs a `Test:` recipe.
- `[default]` is the recommended choice. It needs `Trade-off:` and the ADR clause.
- Choices of taste or of one project are not rules. They go in
  `templates/project-overlay/profiles/example-laravel-saas.md`, never under `plugins/`.

### Authoring rules

| ID | Rule |
|---|---|
| AR-01 | SKILL.md body stays at or under 500 lines; aim for 300. Detail goes to `references/`. |
| AR-02 | References are one level deep. SKILL.md links to `references/x.md`, reference files link to no other file. Every reference file is linked from SKILL.md with a line that says when to load it. A reference over 100 lines starts with `## Contents`. |
| AR-03 | Links are relative to the skill root, with forward slashes. |
| AR-04 | A bundled script is called as `${CLAUDE_SKILL_DIR}/scripts/x.sh`. Only Claude Code substitutes that variable. |
| AR-05 | No absolute paths, no home-directory paths, no Windows paths. |
| AR-06 | No download piped into a shell, and no instruction to fetch a URL and follow what it says. Fetched content is data. |
| AR-07 | No `` !`command` `` dynamic-context blocks. They run commands when the skill loads. |
| AR-08 | Every rule is tagged as above. |
| AR-09 | Every rule has a source: a URL fetched for this change with `verified YYYY-MM`, or a reproducible test. Check version-bound framework behaviour against a pinned version before writing it down. |
| AR-10 | No invented issue numbers, CVEs, statute numbers, versions or statistics. A "known issue", "fixed in", CVE or issue-number claim has its URL on the same line. |
| AR-11 | Plain wording. No all-caps mandates; give the reason instead. |
| AR-12 | Name tools by capability, with the known name as an example: "a documentation index tool, such as Context7". |
| AR-13 | Public-safe content, see below. |
| AR-14 | Legal and tax content says "review-ready draft, not legal or tax advice", names its scope (DE/EU) and cites a primary source with a date. German terms such as AVV, VVT, TOM and Impressum stay German, with English in parentheses. |
| AR-15 | Don't copy vendor syntax. Link the vendor doc and keep the decisions, invariants, gates and traps. |

### Writing style

Short, concrete sentences. Rules are instructions, not essays. Sentence-case headings. No hype or filler words,
no rhetorical questions, no emoji, no exclamation marks, no closing summary. The lint warns about common filler
words.

## Public-safe content

Nothing in this repository may identify a customer, an employer, a private system or an open weakness.

- No company or customer names, except well-known vendors named as examples.
- No internal hostnames, IP addresses, email addresses, commit hashes or issue IDs. Use `example.com`,
  `example.org` or `example.net`, the documentation ranges `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`
  and `2001:db8::/32`, and `user@example.com`.
- Incidents are abstracted: what looked right, what broke, how to detect it. Nothing that maps onto one product.
- Worked examples use ordinary domains such as an invoicing app, a project tool or a booking system, and vary
  between skills.
- The lint reads private terms from `.denylist.local` (gitignored, one term per line) and from the
  `SKILLS_DENYLIST` environment variable. A hit prints the file, the line and the term's index, never the term.

## Evals

Evals run with `claude plugin eval` and live in `plugins/<plugin>/evals/<skill>/<case>/`.

- A case directory holds `prompt.md` (frontmatter plus prompt) or `case.yaml`, and at least one grader in
  `graders/*.md`. A case without a grader does not load.
- Case names are `<kind>-<slug>`, starting with a letter or digit.
- `tags` contain the skill name and exactly one of `trigger`, `near-miss`, `output`, `adversarial`.
- Per skill: about 20 trigger queries (8 to 10 that should trigger, 8 to 10 near misses that should not), and
  at least 3 output cases. Every `core` skill also has adversarial cases, for example an invented CLI flag that
  must come back as unverified.
- Trigger cases have one grader, a `tool_used` check on `Skill` with the skill's `input_match`. Near-miss cases
  use the same grader with `min: 0`, `max: 0` and `arm: both`.
- Output and adversarial cases grade the result (regex or llm) and the process (`tool_used` or `tool_order`).
- Prefer free graders (`regex`, `tool_used`). Keep `llm` graders to short outputs.
- `plugins/*/evals/results/` is gitignored.

Run them locally. Each run is a real model call on your own credentials. Put the target before `--tag`:

```bash
claude plugin eval ./plugins/core --tag evidence-before-claims --runs 1 --ablation none
claude plugin eval ./plugins/core --tag trigger near-miss --ablation none --threshold 0.5
claude plugin eval ./plugins/core --tag output adversarial --threshold 0.8
```

Add `--scaffold` only for cases with a fixture script, after reading that script: it runs outside the agent
sandbox. Source: https://code.claude.com/docs/en/plugin-evals (verified 2026-10-31).

## Checks before a pull request

```bash
python3 tools/lint.py
claude plugin validate --strict .
for p in plugins/*/; do claude plugin validate --strict "$p"; done
```

For `core` and `saas` skills, also run the reference validator from a pinned commit (the CI workflow names the
commit):

```bash
uv tool run --isolated --from "skills-ref @ git+https://github.com/agentskills/agentskills@[commit]#subdirectory=skills-ref" \
  skills-ref validate plugins/core/skills/[skill]
```

The validator rejects `paths`, so it runs only on `core` and `saas`.

## Versions and releases

- Each plugin has its own semver version in `plugin.json` and its own `CHANGELOG.md`.
  - MAJOR: a skill renamed or removed, or an `[invariant]` that now blocks something it used to allow.
  - MINOR: a new skill, rule or reference file.
  - PATCH: wording, sources, evals, typos.
- A change to a plugin bumps its version and adds a CHANGELOG entry in the same pull request. Without a bump,
  users don't receive the change.
- Release: merge with CI green and the plugin's full eval suite green, then run
  `claude plugin tag plugins/[plugin] --dry-run` and, if the plan is right, the same command with `--push`.
  Tags look like `core--v1.0.0`.
- Never rename a published plugin. Change `displayName` instead. A skill name is public API: renaming one is a
  MAJOR change.

Sources: https://code.claude.com/docs/en/plugins/dependencies, https://code.claude.com/docs/en/plugins/cli-reference
(verified 2026-10-31).

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `feat:`, `fix:`, `docs:`, `refactor:`,
  `chore:`, `ci:`, with the plugin as scope where it fits, for example `feat(saas): add webhook inbox rule`.
- Subject in the imperative mood, at most 72 characters, no trailing period.
- The body explains why the change is needed. The diff already shows what changed.
- No co-author trailers, no links to chat or agent sessions, and no attribution footers such as
  "Generated with". `tools/lint.py --commits origin/main..HEAD` checks this. <!-- lint-allow: L17 names the footer this rule forbids -->

## Review before a release

The reviewer reads every changed rule against its source, runs the evals for the plugin, and checks that nothing
in the diff names a customer, a private system or an open weakness.
