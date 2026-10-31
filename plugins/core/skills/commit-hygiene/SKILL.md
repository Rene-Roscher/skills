---
name: commit-hygiene
description: "Writes commits, branch history and pull request text the way a careful colleague would: one logical change, imperative subject, a body that says why, no agent attribution, session links, emoji or filler. Use when committing, amending, squashing, writing a PR description or release notes, or setting up commit hooks and CI checks. Not for what to build or for code review."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Commit hygiene

This skill decides what a commit, a branch history and a pull request description look like, and which
checks keep them that way. Commit tooling and hosting settings stay with their vendors' docs. The failure it
prevents: a history that reads as if an assistant wrote it (long bundled subjects, diff-restating bullet lists,
trailers naming a tool, session links that die with the chat), which costs reviewers time and exposes
internals in public repositories.

## Applies when / does not apply

- Applies: you are about to commit, amend, squash, rebase or push; you write or edit a PR description or a
  squash-merge message; someone sets up a `commit-msg` hook, a CI range check or an attribution setting.
- Does not apply: deciding what to build (`feature-planning`), whether the change is done
  (`verify-before-done`), or whether the push itself is allowed (`safe-actions`). Release notes for customers
  are copy, not commits.

## Rules

- [invariant] No agent attribution anywhere in commits or PRs: no co-author trailer naming a tool, no
  credit line such as "made with [tool]", no session or transcript link, no `Assisted-by` unless the target
  project demands it (last rule). Turn the tool's own default off first, then verify. Why: the default trailers
  of coding agents land in public history and the links point to transcripts nobody else can open. Test: ask
  the agent to commit a small change in a repository whose settings still have the tool default; the message
  contains no trailer naming a tool (eval `output-no-attribution`). Source: vendor defaults and switches in
  [references/agent-switches.md](references/agent-switches.md) (verified 2026-10-31).
- [invariant] Never add `Signed-off-by` for a person. Only a human certifies the Developer Certificate of
  Origin. Why: the trailer is a legal statement by that person. Test: the agent commits for a user whose
  project uses DCO; it tells the user to sign off with `git commit -s` themselves and does not write the
  trailer. Source: https://docs.kernel.org/process/coding-assistants.html (verified 2026-10-31).
- [invariant] One logical change per commit, and each commit builds. If the subject needs "and" to join two
  verbs, or two Conventional Commits types would fit, split it. Why: a reviewer must be able to revert half of
  a change. Test: stage a rename and a bug fix together; the agent commits them separately (eval
  `output-split-commits`). Source: https://docs.kernel.org/process/submitting-patches.html (verified
  2026-10-31).
- [invariant] The subject is imperative, at most 72 characters (aim for 50), has no trailing period and names
  the thing and the effect. "fix bug", "update", "wip", "address review" are not subjects. Why: `git log
  --oneline` and GitHub cut at about 72, and the test is "If applied, this commit will [subject]". Test: the
  `commit-msg` hook in `scripts/` rejects a 90-character subject and `Fixed the login`. Source:
  https://cbea.ms/git-commit/ and the Git project's SubmittingPatches (verified 2026-10-31).
- [invariant] The body says why, not what: the problem, why this approach, what it does not do, numbers for
  performance claims. Leave it out when the subject is enough. No bullet list that restates the diff. Why: the
  diff shows what changed; only the message can say why. Test: delete the body; if nothing is lost, the body
  was filler and should not have been written. Source: https://cbea.ms/git-commit/ (verified 2026-10-31).
- [invariant] No emoji, gitmoji shortcodes, Markdown headings or bold in commit messages, and no filler words
  in the subject (the hook carries the word list). Why: they say
  nothing and mark the text as machine-written. Test: the hook rejects `feat: add export` with a leading
  emoji and a subject made of filler such as "various fixes".
- [invariant] PR descriptions are short and self-contained: one sentence on what changes for whom, a few
  sentences on the problem and approach, a `Tested:` line with what was actually run, a risk line only when
  it is not obvious. No template blocks for a three-line change, no unchecked checklist, no session link. Why:
  the description is copied into the squash commit and read by people without your context. Test: for a
  one-line change the agent writes a description under 80 words without headings (eval `output-pr-body`).
  Source: https://github.com/google/eng-practices/blob/master/review/developer/cl-descriptions.md (verified
  2026-10-31).
- [invariant] Clean history before it is shared: `git commit --fixup` while working, `git rebase -i
  --autosquash` before review, no fixup or squash commits left at merge time, no force-push of a branch others
  have pulled. Why: rewriting shared history breaks other people's clones. Test: CI fails a range that
  contains a fixup commit; the agent asks before any force-push (see `safe-actions`).
- [invariant] Link issues in footers, not in the subject: `Refs: #7` while work continues, `Closes: #7`
  on the change that finishes it. Closing keywords only act on a PR that targets the default branch. Why: a
  `fix #7` subject reads as noise and closes nothing in a release-branch PR. Test: the subject contains no
  `#` number. Source: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
  (verified 2026-10-31).
- [default] Conventional Commits 1.0.0 prefixes (`feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`,
  `ci`, `chore`, `revert`), scope in parentheses, an exclamation mark after the type or a breaking-change footer for breaking changes,
  lowercase after the colon. `chore` never carries a behaviour change. Trade-off: a prefix costs 6 to 12
  characters of the subject. Deviate only with an ADR that names this trade-off; follow the repository's
  existing convention first. Source: https://www.conventionalcommits.org/en/v1.0.0/ (verified 2026-10-31).
- [default] Squash merges take the PR title and commit details, not "title and description", and the message is
  read before the merge button is pressed. Trade-off: the description no longer lands in history verbatim.
  Deviate only with an ADR that names this trade-off. Source:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
  (verified 2026-10-31).
- [default] Sign commits (SSH signing is the simplest) and turn on branch protection for signed commits.
  Trade-off: every contributor sets up a key. Deviate only with an ADR that names this trade-off. An agent
  committing on a person's machine signs with that person's key, so review before committing. Source:
  https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification
  (verified 2026-10-31).
- [invariant] Read the target repository's CONTRIBUTING file before the first commit. If it requires an
  AI-disclosure trailer, write exactly that trailer and nothing else, and tell the user. Why: some upstreams
  (the Linux kernel asks for `Assisted-by: LLM [TOOL]`) reject undisclosed AI contributions, and a skill that
  hides use there does harm. Test: in a repository whose CONTRIBUTING asks for `Assisted-by`, the agent writes
  that trailer and no other attribution. Source: https://docs.kernel.org/process/coding-assistants.html
  (verified 2026-10-31).

## Procedure

1. Read the repository's existing convention: `git log --oneline -20`, CONTRIBUTING, any hook or commitlint
   config. Follow it where it differs from the defaults here.
2. Check that the tool's attribution default is off, see [references/agent-switches.md](references/agent-switches.md).
   Fix the setting once; do not rely on remembering per commit.
3. Stage by file or hunk, never with a blanket `git add -A` over unrelated work. Read `git diff --cached`
   and split if it holds more than one change.
4. Write the subject first, then a body only if the why is not obvious. Read it aloud with "If applied, this
   commit will" in front.
5. For a PR, write the description from the finished diff, not from memory, and run the PR-body check.
6. To enforce all of this, propose the hook and CI range check to the owner, see
   [references/enforcement.md](references/enforcement.md). Install them only when asked.

## Traps

- A squash merge of a one-commit PR with the default message: the trailer from the commit lands on `main`.
- `git commit --no-verify`, which some agents use by default, skips the hook. The CI range check is the
  guarantee, the hook is the convenience.
- Cloud agents that commit on the host side never run local hooks.
- A body that lists every touched file under "Changes".
- A `chore:` commit that changes behaviour and so vanishes from the changelog.
- Rewriting a branch after review has started, which orphans review comments.
- Committed agent instruction files in a public repository.

## Done when

- The commit or PR text passes `scripts/commit-msg` and `scripts/check-pr-body`.
- Every commit has one logical change and builds.
- No attribution, link or emoji is in the message, the PR body or the squash message.
- Any repository-specific convention or disclosure rule was followed and mentioned to the user.

## References

- [references/agent-switches.md](references/agent-switches.md): read when you must turn off or verify the
  attribution of a specific agent, or when a cloud surface ignores local settings.
- [references/enforcement.md](references/enforcement.md): read when setting up the `commit-msg` hook, the CI
  range check or the PR-body check, and when changing the squash default.

## Sources

- https://www.conventionalcommits.org/en/v1.0.0/: format, types, footers, breaking changes, verified 2026-10-31.
- https://cbea.ms/git-commit/: subject limits, imperative mood, why over what, verified 2026-10-31.
- https://github.com/git/git/blob/master/Documentation/SubmittingPatches: trailers, why over what, AI
  section, verified 2026-10-31.
- https://docs.kernel.org/process/submitting-patches.html and
  https://docs.kernel.org/process/coding-assistants.html: one change per patch, `Assisted-by`, no agent
  `Signed-off-by`, verified 2026-10-31.
- https://github.com/google/eng-practices/blob/master/review/developer/cl-descriptions.md: what a change
  description must say, verified 2026-10-31.
