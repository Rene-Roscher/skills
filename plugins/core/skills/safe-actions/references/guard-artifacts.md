# Guard artifacts

Checks that make the safe-actions rules hold in a project without relying on the agent remembering them. Add them
to the target repository with the owner's approval; each one is a change to shared configuration.

## Contents

- Action matrix file
- Committed permission settings
- PreToolUse hook for the hard cases
- Test-environment transport guard
- Dev-config channel check
- Secret scanner
- CODEOWNERS for platform-wide paths
- Per-session test database

## Action matrix file

`docs/agents/action-matrix.md` (or the path the project prefers), filled from the template: tiers, substitutes,
canonical locations, read-access runbook, outbound channels per environment. The project facts file and the
AGENTS.md snippet point to it.

## Committed permission settings

`.claude/settings.json` in the repository, with:

- deny rules for the never tier, including secret paths (`.env` files, key files, kubeconfigs, credential stores);
- ask rules for the approval tier: push, tag, release and publish commands, cluster and IaC write verbs, volume
  removal, process kill, destructive git commands, database wipe or reset commands.

A CI check reads the matrix and the settings and fails when a never row has neither an enforcement entry nor a
written reason.

## PreToolUse hook for the hard cases

A POSIX sh or Python script without network access that blocks:

- force-push to protected branches in any spelling;
- download piped into a shell;
- cluster write verbs against production contexts;
- reads of secret files through commands the Read rules don't cover.

It fails closed: when it can't parse the tool input, it blocks and says why.

## Test-environment transport guard

A test that runs in the normal suite and asserts that, under the test and dev configuration, every outbound
transport resolves to a fake, log, array or sink driver: mail (every mailer the code can select), SMS, voice,
push, chat, outgoing webhooks and the payment client. It checks the transport resolved at send time, not only the
config value, because per-message transport choices can override an environment-wide setting.

Recipe: for each channel, build the client the way production code does, send one message, and assert it was
captured by the fake or sink and no network connection was opened.

## Dev-config channel check

A script that lists every outbound channel in each non-production configuration and the provider it points to. It
fails when a channel points at a real provider unless the matrix lists that channel with a reason. Run it in CI and
before seeding data that is built to fail.

## Secret scanner

A secret scanner (for example gitleaks) in pre-commit and in CI, with the same configuration in both. CI is the one
that counts, because local hooks can be skipped.

## CODEOWNERS for platform-wide paths

CODEOWNERS entries that require the owner's review for shared templates (all mails, all layouts), app-wide
middleware and rate limiters, authentication and authorization gates, base CI workflows and shared infrastructure
modules. Together with branch protection, this turns the "report and ask" rule into a merge requirement.

## Per-session test database

The test bootstrap derives the test database name from a per-session variable (for example a session or worktree
ID) and refuses to run on the shared default name when another run holds it. Two runs on one test database drop
each other's tables and produce failures that look real.
