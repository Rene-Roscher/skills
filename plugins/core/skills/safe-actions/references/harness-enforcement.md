# Harness enforcement

Skill text and CLAUDE.md shape what the agent tries. They don't decide what runs. In Claude Code, permission rules,
hooks and the sandbox decide. Mirror the matrix into them so the boundary holds even when a skill does not load.
Syntax lives in the vendor docs linked below; this file covers the mapping and the gaps.

## Mapping the matrix

| Matrix tier | Enforcement |
|---|---|
| Never | `deny` rules, plus a PreToolUse hook where the check needs argument parsing |
| Approval per action | `ask` rules, plus a hook for commands that can be written several ways |
| Allowed | `allow` rules for the commands the project runs often |

Commit the project settings file (`.claude/settings.json`) with these rules so every developer and CI session gets
them. Keep personal additions in the local settings file.

## Facts that shape the rules (Claude Code)

- Rules are evaluated deny, then ask, then allow. The first match in that order decides, and specificity does not
  change the order.
- A PreToolUse hook does not bypass permission rules: a matching deny rule still blocks, and a matching ask rule
  still prompts, even when the hook returned allow.
- A hook that exits with code 2 blocks the call before rules are evaluated, so it can block a call an allow rule
  would let through.
- Bash argument patterns are fragile. `Bash(git push *)` does not match `git -C . push origin main`,
  `git -c push.default=current push origin main` or `git 'push' origin main`. Use a hook or the sandbox for hard
  boundaries.
- `Read` deny rules cover Claude's file tools, the file commands Claude Code recognizes in Bash (such as `cat`,
  `head`, `tail`, `sed`, `tee`) and redirection targets. They do not cover a command that reads files without
  naming them, such as `grep -r pattern .`, or a script that opens files itself. The sandbox enforces paths for
  every process.
- A bare filename in a `Read` rule matches at any depth, so `Read(.env)` and `Read(**/.env)` are the same.
- A deny or ask pattern that starts with `!` carves paths out of the rules listed before it in the same settings
  file, for example `Read(.env.*)` followed by `Read(!.env.example)`.

## What to put in hooks

Hooks are for checks a pattern can't express:

- Force-push to protected branches, in any spelling (`--force`, `-f`, `+refspec`).
- Pipe-to-shell installs.
- Cluster write verbs against production contexts, including `--context` given late on the command line.
- Reads of secret files through commands the Read rules don't cover.

Keep hooks free of network calls, and fail closed: when the hook can't parse the input, block and say why.

## Auditing

- A CI check compares the matrix with the settings: every never row has a deny rule or hook, or a written reason
  why it can't be enforced.
- Review new allow rules like code. An allow rule that matches a wrapper (`Bash(make *)`) allows everything the
  wrapper runs.
- Clients without permission rules record the gap in an ADR and rely on the sandbox or a wrapper script.

## Sources

- https://code.claude.com/docs/en/permissions: evaluation order, hook precedence, exit code 2, Bash pattern limits,
  Read rule scope, `!` carve-outs; verified 2026-10.
- https://code.claude.com/docs/en/hooks: hook events and input format.
- https://code.claude.com/docs/en/sandboxing: filesystem and network limits for every process.
