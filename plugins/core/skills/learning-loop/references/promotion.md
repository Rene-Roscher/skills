# Promoting a lesson into an enforcing artifact

Load when a lesson recurs and you pick, build and prove the artifact that enforces it.

## When to promote

Promote when any of these happens (the first three are the triggers the Claude Code memory docs list for
adding an instruction; the artifact is the next step for a lesson that already existed):

- The agent makes the same mistake a second time.
- A code review catches the same thing again.
- The user types the same correction again.
- The mistake would cost money, data or security the first time it slips through. Then build the artifact
  right away.

## Pick the artifact

| Shape of the mistake | Artifact | Example in an invoicing app |
|---|---|---|
| A code pattern | architecture test, lint rule, or a structural rule such as an ast-grep rule run in CI | a test fails when a migration declares an amount column as float |
| A command that must never run | permission deny rule, or a PreToolUse hook that exits 2 or returns `permissionDecision: "deny"` | block a formatter run whose target is a directory |
| An environment mismatch | a check in the test bootstrap that aborts the run | abort when the runtime minor version differs from the production pin |
| A rule that spans files | a CI script that fails the build | every table behind an API resource has a public ID column |
| A step that gets skipped | a CI check, or a Stop hook that reminds or blocks | migrations exist for every model change before tests run |

Prefer the artifact closest to where the mistake is made: a hook stops the command before it runs, a test stops
the merge, a CI gate stops the release.

Sources: Claude Code memory docs ("Claude treats them as context, not enforced configuration. To block an
action regardless of what Claude decides, use a PreToolUse hook instead.") and hooks docs (exit code 2 on
PreToolUse blocks the tool call, stderr is the message; `permissionDecision` allow, deny, ask or defer), both
https://code.claude.com/docs/en/, verified 2026-10-31. Hook syntax lives in the hooks docs; do not copy it into
lessons.

## Prove it

1. Write the artifact.
2. Reintroduce the mistake in a scratch change (a float column, the forbidden command, the wrong runtime).
3. The artifact fails with a message that names the rule and the fix.
4. Revert the scratch change. The artifact passes.
5. Record the proof command in the lesson.

An artifact that never failed has not been shown to work.

## Test under production conditions

A guard can pass in the suite and never fire in production when the test world differs:

- queued work runs synchronously in tests and later in production;
- an in-memory database accepts what the production engine rejects, or orders rows differently;
- a frozen or mocked clock hides second boundaries;
- a fake client returns what the real one never sends.

Run the guard's test with the production behaviour forced: fake the queue so nothing runs inline, use the
production database engine, use a real clock. If the guard depends on data written asynchronously, base it on
data written in the same transaction instead.

## After promotion

- Shrink the lesson: rule, Why, the trigger, and a pointer to the artifact with its path.
- Keep the Why. Without it, someone deletes the test as noise.
- Update the index line to mention the artifact.
