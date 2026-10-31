# Self-hosted runners

## Boundaries

- No self-hosted runners on public repositories. A fork pull request can run code on the machine. GitHub
  recommends self-hosted runners only for private repositories.
- A persistent runner can be compromised by one untrusted job for every later job, and GitHub cannot guarantee that
  a self-hosted runner runs only one job. So jobs with `id-token: write`, write scopes or production secrets never
  share a persistent runner with pull-request jobs, scheduled jobs from other repositories, or anything else less
  trusted.
- For release work, use ephemeral runners (one job, then the runner is removed) or just-in-time runners created
  through the REST API for a single job, in a runner group reserved for release.
- Restrict runner groups to selected repositories. GitHub's docs also mention restricting which workflows can use
  a group; check that your plan offers it before you rely on it.

## Host isolation

- No Docker socket mounted into jobs. Access to the socket is root on the host.
- No host networking and no shared tool cache or work directory between trust levels.
- Service containers on a shared host collide on fixed host ports. Let the runtime assign the host port and read
  it from the job context, or isolate jobs per host.
- Clean the work directory between jobs on any runner that is not ephemeral.

## Runner selection switches

A pattern such as `runs-on: ${{ vars.CI_RUNNER || 'ubuntu-latest' }}` lets a repository move CI to self-hosted
runners when hosted runners are unavailable. It must not move signing or deploy jobs:

- Jobs with `id-token: write`, write scopes or deploy secrets use a fixed label from the release allowlist, not
  the switch.
- A preflight step on switched jobs prints the runner name and labels and fails if the label is not on the
  expected list.
- The workflow checker fails a privileged job whose `runs-on` is an expression or a label outside the allowlist.

## Audit, read-only

```bash
gh api orgs/ORG/actions/runner-groups --paginate
gh api orgs/ORG/actions/runner-groups/GROUP_ID/repositories --paginate
gh api repos/OWNER/REPO/actions/runners --paginate
```

Compare the output with the intended layout: which groups exist, which repositories can use each group, and
whether release runners are ephemeral. Hand differences to an administrator; don't change runner groups from an
agent session.

## Sources

- https://docs.github.com/en/actions/reference/security/secure-use (verified 2026-10)
- https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access (verified 2026-10)
- https://docs.zizmor.sh/audits/ (`self-hosted-runner`, pedantic persona) (verified 2026-10)
