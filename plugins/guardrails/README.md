# guardrails

An optional plugin with no skills, only hooks. It enforces two rules from `core` that a prompt alone cannot
guarantee, because a model under pressure can talk itself out of them:

- **Attempt cap** (`goal-focus`, `know-your-limits`). Every failed shell command that is not a read-only probe
  counts as one attempt. After each failure the agent sees `attempt k/10`; from the third attempt it is
  reminded to stop if nothing new was learned. At the tenth attempt it is told to undo what it cannot explain
  and write the stop report, and from then on every edit and every command except read-only probes (`grep`,
  `ls`, `cat`, `git diff`, `git log` and similar) is denied until you reply. A passing check (test, lint, type
  check, build, validator) resets the count, and so does every message from you.
- **No bypassed checks** (`verify-before-done`, `know-your-limits`). Commands that skip or silence a check are
  denied: `git commit --no-verify`, `git commit -n`, `git push --no-verify`, `-c core.hooksPath=…`, `HUSKY=0`,
  `LEFTHOOK=0`, `SKIP=…` before a commit, and a check runner followed by `|| true`, `|| :` or `|| exit 0`.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install guardrails@rene-roscher-skills
```

Requires `python3` (3.8 or newer) on `PATH`; the script uses the standard library only.

## Settings

| Variable | Default | Effect |
|---|---|---|
| `GUARDRAILS_ATTEMPT_CAP` | `10` | Failed attempts before the stop. |

Counters live in the plugin's data directory (`CLAUDE_PLUGIN_DATA`, else the temp directory), one file per
session, with a separate count for each subagent. Files older than seven days are removed.

## How it decides

- A failure is a Bash call that reaches `PostToolUseFailure` (non-zero exit). Interrupted calls and commands
  made only of read-only probes do not count, so a `grep` without a match is not an attempt.
- A check is a command that runs a known test, lint, type, build or validation tool (`pest`, `phpunit`,
  `pytest`, `jest`, `vitest`, `go test`, `cargo test`, `npm test`, `eslint`, `tsc`, `phpstan`, `ruff`, `make`,
  `--self-test` and others). Only a passing check resets the count; a successful `curl` does not.
- If the hook itself fails (bad input, unreadable state), it exits without output and never blocks the session.

## Check it

```bash
python3 plugins/guardrails/hooks/guard.py --self-test
```

The self-test runs offline: it replays a fix loop to the cap, the reset by a passing check and by your reply,
and the bypass patterns, including commands that must stay allowed (`git commit -m 'explain the -n flag'`,
`grep … || true`).

## Limits

- It counts commands, not reasons. Ten failures on unrelated problems in one turn also reach the cap; reply to
  continue.
- It parses shell text. A check started through a script with an unfamiliar name is not recognised as a check,
  and a bypass hidden inside a script file is not seen.
- Hooks follow the Claude Code hook interface; other agent runtimes ignore this plugin.

Source: https://code.claude.com/docs/en/hooks (`PreToolUse` deny, `PostToolUseFailure` with
`additionalContext`, plugin `hooks/hooks.json`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`), verified
2026-11-04.
