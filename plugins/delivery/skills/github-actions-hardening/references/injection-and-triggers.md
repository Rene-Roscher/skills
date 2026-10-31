# Injection and privileged triggers

## Expressions in shell code

`${{ }}` expands as text before the shell sees the line. Pass values through `env:` and quote them:

```yaml
- name: Check title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: |
    printf '%s\n' "$PR_TITLE" | grep -Eq '^(feat|fix|docs|chore)(\(.+\))?: '
```

Treat these as untrusted, including the ones that look internal:

- anything under `github.event` that a user can type: titles, bodies, comments, labels, commit messages, author
  names, branch names;
- `github.head_ref`, `github.ref_name` (anyone who can push a branch or tag chooses it);
- `inputs.*` of `workflow_dispatch` and `workflow_call`;
- step outputs and job outputs computed from any of the above;
- the contents of artifacts and caches written by a less privileged workflow.

The same applies to `actions/github-script`: read values from `process.env`, not from `${{ }}` inside `script:`.

Values that are safe to expand in `run:` are the ones no external party controls, such as `runner.temp`,
`runner.os`, `github.run_id` and literal secrets references passed through `env:`. Keep that allowlist in the
workflow checker.

`GITHUB_ENV` and `GITHUB_PATH` are read by every later step. A write such as
`echo "NAME=$UNTRUSTED" >> "$GITHUB_ENV"` lets the input set `LD_PRELOAD` or `NODE_OPTIONS` for the rest of the
job. zizmor `github-env` reports these writes.

## Privileged triggers

`pull_request_target`, `workflow_run` and `issue_comment` run with the base repository's token and secrets.

Platform behaviour to know (checked 2026-10-31):

- Since 2025-12-08 the `pull_request_target` workflow file and its default checkout come from the default branch,
  and `GITHUB_REF` resolves to the default branch. Environment branch rules for `pull_request_target` evaluate
  against the default branch, and for `pull_request` against `refs/pull/[number]/merge`.
- Workflow execution protections (GA 2026-09-17) let enterprises, organizations and repositories allowlist who may
  trigger workflows (actor rules) and which events may start them (event rules). The changelog names the REST
  API at all three levels and links GitHub's "Control workflow execution" docs for the details.
- For public repositories without an applicable event policy, GitHub adds a default rule that disables
  `pull_request_target`. It starts in evaluate mode; enforcement for affected repositories starts 2026-12-02 (the
  date was updated on 2026-10-21). Private and internal repositories are not affected. To keep such a workflow,
  allow `pull_request_target` in an event policy, optionally only for specific workflow files.
- The changelog names no plans for execution protections. Check your plan before you rely on them.

## The split pattern

For a job that must comment on fork pull requests (coverage, size reports):

1. Workflow A, `on: pull_request`, `permissions: contents: read`: checks out the head, runs the tests, writes the
   result to a file with a fixed format (for example one integer), and uploads it as an artifact.
2. Workflow B, `on: workflow_run` for workflow A, `permissions: pull-requests: write` on the commenting job only:
   downloads the artifact into `${{ runner.temp }}`, never into the workspace, parses it strictly (reject anything
   that is not the expected format), and posts the comment. It never checks out the pull-request head and never
   runs a build, install or test step.

Bot checks read `github.event.pull_request.user.login`. `github.actor` is whoever caused the latest event, which
can be a human re-running a bot's workflow. zizmor `bot-conditions` reports spoofable checks.

## Caches between trust levels

A workflow that runs pull-request code can write cache entries that a privileged workflow on the default branch
later restores. Privileged workflows don't restore caches that untrusted runs could have written, and release
workflows read no cache at all. zizmor `cache-poisoning` covers the common cases.

## Sources

- https://docs.github.com/en/actions/reference/security/secure-use (verified 2026-10)
- https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target (verified 2026-10)
- https://github.blog/changelog/2025-11-07-actions-pull_request_target-and-environment-branch-protections-changes/ (verified 2026-10)
- https://github.blog/changelog/2026-09-17-workflow-execution-protections-in-github-actions-generally-available/ (verified 2026-10)
- https://docs.zizmor.sh/audits/ (verified 2026-10)
