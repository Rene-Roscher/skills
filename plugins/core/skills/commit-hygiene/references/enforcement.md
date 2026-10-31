# Enforcement

Load when setting up the `commit-msg` hook, the CI range check or the PR-body check, and when changing the
squash default. Propose these to the owner; create them only when asked. The scripts are POSIX sh, need only
git, and run under `LC_ALL=C` so emoji match as bytes.

## Scripts

| Script | Job | Exit |
|---|---|---|
| `scripts/commit-msg` | Rejects agent identity in `*-by:` trailers, "made with [tool]" lines, session trailers and agent links, emoji, over-long or non-imperative subjects, filler words in the subject. Warns on 4 or more bullet lines, filler in the body, Markdown headings, lines over 72 characters | 0 accept, 1 reject |
| `scripts/check-range` | Runs the hook over every non-merge commit in a range, flags agent author or committer identities and leftover `fixup!` commits | 0 clean, 1 finding, 2 usage |
| `scripts/check-pr-body` | Rejects attribution lines, session links and emoji in the PR body read from `PR_BODY` | 0 clean, 1 finding |
| `scripts/self-test` | Proves the three scripts accept good input and reject traces, in a temporary repository | 1 on any mismatch |

Run `sh scripts/self-test` after any change to a script. It makes no network calls.

## Install the hook

Hooks are not cloned, so every clone runs this once:

```sh
mkdir -p .githooks && cp commit-msg .githooks/ && chmod +x .githooks/commit-msg
git config core.hooksPath .githooks
```

Per-repository opt-outs through `git config`:

- `hooks.commitmsg.allowAiDisclosure true` when the project requires a disclosure trailer.
- `hooks.commitmsg.maxSubject 72` to change the hard subject limit.

`git commit --no-verify` skips the hook, so CI runs the same checks.

## CI

```yaml
- uses: actions/checkout@<full-commit-sha>
  with:
    fetch-depth: 0
    persist-credentials: false
- run: sh .githooks/check-range "origin/${BASE_REF}" HEAD
  env:
    BASE_REF: ${{ github.base_ref }}
- run: sh .githooks/check-pr-body
  env:
    PR_BODY: ${{ github.event.pull_request.body }}
```

Pass the body and the base ref through `env:`, never by interpolating the expression into `run:`: a PR title
or body is attacker-controlled text. Pin actions to a full commit SHA as `github-actions-hardening` describes.

## Repository settings

- Squash default: "pull request title" or "title and commit details".
- Branch protection: require the check above, require signed commits where the team signs.
- A post-merge job that runs the hook over `git log -1 --format=%B` of the default branch can alert; it cannot
  block.

## False positives

The subject word list is deliberately short. Some of the words are real terms in specialist code. Disable a word per
repository by editing the `filler` pattern in the copied hook, not by passing `--no-verify`.
